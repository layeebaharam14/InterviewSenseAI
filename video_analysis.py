"""
video_analysis.py — InterviewSense AI
Phase 3: Advanced Facial, Eye-Gaze and Posture Analysis Module

Provides:
1. Multi-modal facial presence detection (face count, visibility %, centering %).
2. Head-pose estimation (Pitch, Yaw, Roll, forward-facing %, natural movement tracking).
3. Eye-gaze estimation (MediaPipe Face Mesh landmark-based camera-facing approximation).
4. Posture analysis (MediaPipe Pose shoulder alignment, tilt, upper-body presence).
5. Per-question structured analytics with transparent, non-hallucinating metrics.
6. Weighted overall visual performance aggregation across questions.
7. Full backward-compatibility with aggregate_video_analysis(frames) for Mock HR Interview.
"""

import cv2
import numpy as np

# Ensure protobuf 5+/7+ compatibility with MediaPipe legacy solutions
try:
    import google._upb._message as upb
    if hasattr(upb, 'FieldDescriptor') and not hasattr(upb.FieldDescriptor, 'label'):
        upb.FieldDescriptor.label = property(lambda self: getattr(self, '_label', 1))
except Exception:
    pass

import mediapipe as mp

# =============================================================================
# MODEL INITIALIZATION (Reused across calls for efficiency)
# =============================================================================

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

try:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    )
except Exception:
    face_mesh = None

try:
    mp_pose = mp.solutions.pose
    pose_tracker = mp_pose.Pose(
        static_image_mode=True,
        min_detection_confidence=0.5
    )
except Exception:
    pose_tracker = None

# 3D model reference points for head pose estimation (in mm relative to nose)
_3D_MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip (index 1)
    (0.0, -330.0, -65.0),        # Chin (index 152)
    (-225.0, 170.0, -135.0),     # Left eye outer corner (index 33)
    (225.0, 170.0, -135.0),      # Right eye outer corner (index 263)
    (-150.0, -150.0, -125.0),    # Left mouth corner (index 61)
    (150.0, -150.0, -125.0)      # Right mouth corner (index 291)
], dtype=np.float64)

# Key landmark indices in MediaPipe Face Mesh
_LANDMARK_INDICES = [1, 152, 33, 263, 61, 291]


# =============================================================================
# 1. HEAD-POSE ESTIMATION
# =============================================================================

def _estimate_head_pose(landmarks, image_shape):
    """
    Estimates head yaw, pitch, and roll in degrees using cv2.solvePnP.
    Returns (yaw, pitch, roll, orientation_label) or (None, None, None, 'unavailable').
    """
    h, w = image_shape[:2]
    try:
        image_points = np.array([
            (landmarks[idx].x * w, landmarks[idx].y * h)
            for idx in _LANDMARK_INDICES
        ], dtype=np.float64)

        focal_length = w
        center = (w / 2.0, h / 2.0)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))

        success, rotation_vector, _ = cv2.solvePnP(
            _3D_MODEL_POINTS, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return None, None, None, "unavailable"

        rot_mat, _ = cv2.Rodrigues(rotation_vector)
        proj_matrix = np.hstack((rot_mat, np.zeros((3, 1))))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)
        pitch = float(euler_angles[0][0])
        yaw = float(euler_angles[1][0])
        roll = float(euler_angles[2][0])

        # Head orientation categorization
        if abs(yaw) <= 18.0 and abs(pitch) <= 18.0:
            orientation = "forward"
        elif yaw < -18.0:
            orientation = "turned right"
        elif yaw > 18.0:
            orientation = "turned left"
        elif pitch < -18.0:
            orientation = "tilted up"
        else:
            orientation = "tilted down"

        return yaw, pitch, roll, orientation
    except Exception:
        return None, None, None, "unavailable"


# =============================================================================
# 2. EYE-GAZE ESTIMATION (LANDMARK-BASED APPROXIMATION)
# =============================================================================

def _estimate_iris_gaze(landmarks, image_shape):
    """
    Computes approximate horizontal and vertical gaze ratio using refined eye & iris landmarks.
    Left eye: iris 468, corners 33, 133
    Right eye: iris 473, corners 362, 263
    Returns (approx_direction: str, is_camera_facing: bool, iris_detected: bool)
    """
    try:
        # Check if iris landmarks are present (requires refine_landmarks=True)
        if len(landmarks) > 473:
            lx_iris = landmarks[468].x
            rx_iris = landmarks[473].x

            lx_outer = landmarks[33].x
            lx_inner = landmarks[133].x
            rx_inner = landmarks[362].x
            rx_outer = landmarks[263].x

            # Compute horizontal ratios within eye bounding span
            l_width = max(1e-4, abs(lx_inner - lx_outer))
            r_width = max(1e-4, abs(rx_outer - rx_inner))

            l_ratio = (lx_iris - min(lx_outer, lx_inner)) / l_width
            r_ratio = (rx_iris - min(rx_outer, rx_inner)) / r_width

            avg_ratio = (l_ratio + r_ratio) / 2.0

            # 0.40 - 0.60 indicates pupil is approximately centered in socket
            if 0.38 <= avg_ratio <= 0.62:
                gaze_dir = "direct / camera-facing"
                is_facing = True
            elif avg_ratio < 0.38:
                gaze_dir = "looking left"
                is_facing = False
            else:
                gaze_dir = "looking right"
                is_facing = False

            return gaze_dir, is_facing, True
    except Exception:
        pass

    return "approximate forward", True, False


# =============================================================================
# 3. POSTURE ANALYSIS (SHOULDER ALIGNMENT & UPPER-BODY VISIBILITY)
# =============================================================================

def _estimate_posture(image):
    """
    Estimates candidate posture via MediaPipe Pose (shoulder alignment).
    Returns (status: str, tilt_deg: float|None, upper_body_visible: bool, message: str)
    """
    if pose_tracker is None:
        return "unavailable", None, False, "Posture analysis unavailable because Pose model could not be initialized."
    try:
        results = pose_tracker.process(image)
        if not results.pose_landmarks:
            return "unavailable", None, False, "Posture analysis unavailable because the upper body was not sufficiently visible."
        landmarks = results.pose_landmarks.landmark
        l_shoulder = landmarks[11]
        r_shoulder = landmarks[12]

        l_vis = getattr(l_shoulder, 'visibility', 0.0)
        r_vis = getattr(r_shoulder, 'visibility', 0.0)

        # Upper body must have both shoulders sufficiently visible
        if l_vis >= 0.5 and r_vis >= 0.5:
            dy = r_shoulder.y - l_shoulder.y
            dx = r_shoulder.x - l_shoulder.x
            angle = abs(np.degrees(np.arctan2(dy, dx)))
            tilt = min(angle, abs(180.0 - angle))
            tilt = round(float(tilt), 1)

            if tilt < 8.0:
                status = "Upright and well-aligned"
                msg = f"Shoulders are level and upright (tilt: {tilt}°)."
            elif tilt < 15.0:
                status = "Slight shoulder tilt"
                msg = f"Slight natural shoulder tilt detected (tilt: {tilt}°)."
            else:
                status = "Notable shoulder tilt"
                msg = f"Noticeable lateral shoulder tilt detected (tilt: {tilt}°)."

            return status, tilt, True, msg

        return "unavailable", None, False, "Posture analysis unavailable because the upper body was not sufficiently visible."
    except Exception as e:
        return "unavailable", None, False, f"Posture analysis unavailable ({e})."


# =============================================================================
# 4. SINGLE FRAME ANALYSIS
# =============================================================================

def analyze_frame(image):
    """
    Analyzes a single RGB numpy array frame.
    Gracefully handles empty, low-light, or corrupted frames.
    Returns backward-compatible dictionary for all consumers.
    """
    # Safe validation for frame integrity
    if image is None or not isinstance(image, np.ndarray) or image.size == 0 or len(image.shape) < 3:
        return {
            "face_detected": False,
            "eye_contact": "poor",
            "movement": "high",
            "multiple_faces": False,
            "detected_face_count": 0,
            "face_position": "unavailable",
            "is_centered": False,
            "head_pose": {"yaw": None, "pitch": None, "roll": None, "orientation": "unavailable", "is_forward": False},
            "eye_gaze": {"direction": "unavailable", "is_camera_facing": False, "iris_detected": False},
            "posture": {"status": "unavailable", "tilt_deg": None, "upper_body_visible": False, "message": "Posture analysis unavailable."},
            "center_coords": (0.5, 0.5)
        }

    face_detected = False
    eye_contact = "poor"
    movement = "high"
    multiple_faces = False
    detected_face_count = 0
    face_position = "unavailable"
    is_centered = False
    center_coords = (0.5, 0.5)

    head_pose = {"yaw": None, "pitch": None, "roll": None, "orientation": "unavailable", "is_forward": False}
    eye_gaze = {"direction": "unavailable", "is_camera_facing": False, "iris_detected": False}
    posture_data = {"status": "unavailable", "tilt_deg": None, "upper_body_visible": False, "message": "Posture analysis unavailable."}

    try:
        detection_results = face_detection.process(image)
        if detection_results and detection_results.detections:
            face_detected = True
            detected_face_count = len(detection_results.detections)
            multiple_faces = (detected_face_count > 1)

            # Primary face bounding box analysis
            bboxC = detection_results.detections[0].location_data.relative_bounding_box
            xc = bboxC.xmin + (bboxC.width / 2.0)
            yc = bboxC.ymin + (bboxC.height / 2.0)
            center_coords = (float(xc), float(yc))

            # Centering estimation
            is_centered = (0.32 <= xc <= 0.68 and 0.18 <= yc <= 0.82)
            if is_centered:
                face_position = "centered"
            elif xc < 0.32:
                face_position = "off-center left"
            elif xc > 0.68:
                face_position = "off-center right"
            elif yc < 0.18:
                face_position = "off-center high"
            else:
                face_position = "off-center low"

            is_central = (0.22 < xc < 0.78 and 0.15 < yc < 0.85)
            eye_contact = "good" if is_central else "poor"
            movement = "low" if is_central else "high"

            # Face Mesh: 3D head pose and gaze estimation
            if face_mesh is not None:
                try:
                    mesh_results = face_mesh.process(image)
                    if mesh_results and mesh_results.multi_face_landmarks:
                        face_lms = mesh_results.multi_face_landmarks[0].landmark
                        yaw, pitch, roll, orientation = _estimate_head_pose(face_lms, image.shape)
                        gaze_dir, is_gaze_facing, iris_detected = _estimate_iris_gaze(face_lms, image.shape)

                        if orientation != "unavailable":
                            is_forward = (orientation == "forward")
                            head_pose = {
                                "yaw": round(yaw, 1),
                                "pitch": round(pitch, 1),
                                "roll": round(roll, 1),
                                "orientation": orientation,
                                "is_forward": is_forward
                            }
                            eye_gaze = {
                                "direction": gaze_dir,
                                "is_camera_facing": is_forward and is_gaze_facing,
                                "iris_detected": iris_detected
                            }
                            # Refined backward-compatible eye contact
                            if is_forward and is_gaze_facing and is_central:
                                eye_contact = "good"
                            else:
                                eye_contact = "poor"
                except Exception:
                    pass

            # Posture check
            p_status, p_tilt, p_vis, p_msg = _estimate_posture(image)
            posture_data = {
                "status": p_status,
                "tilt_deg": p_tilt,
                "upper_body_visible": p_vis,
                "message": p_msg
            }
    except Exception:
        pass

    return {
        # Core backward-compatible keys
        "face_detected": face_detected,
        "eye_contact": eye_contact,
        "movement": movement,
        "multiple_faces": multiple_faces,
        "detected_face_count": detected_face_count,
        "face_position": face_position,
        "is_centered": is_centered,
        "head_pose": head_pose,
        "eye_gaze": eye_gaze,
        "posture": posture_data,
        "center_coords": center_coords
    }


# =============================================================================
# 5. PER-QUESTION COMPREHENSIVE VISUAL ANALYSIS
# =============================================================================

def analyze_technical_question_frames(frames, question_id=1, domain="", skill=""):
    """
    Performs full visual analysis on frames collected during a technical question.
    Calculates face visibility, head pose, gaze estimation, posture, and natural movement.
    Produces human-readable observations without inferring emotion, honesty, or personality.
    """
    total = len(frames) if frames else 0
    if total == 0:
        return {
            "question_id": question_id,
            "domain": domain,
            "skill": skill,
            "total_frames": 0,
            "face_frames": 0,
            "face_visibility_pct": 0.0,
            "face_centering_pct": 0.0,
            "multiple_faces_detected": False,
            "multiple_face_occurrences": 0,
            "max_consecutive_no_face_frames": 0,
            "head_pose_summary": {
                "forward_facing_pct": 0.0,
                "average_yaw": 0.0,
                "average_pitch": 0.0,
                "average_roll": 0.0,
                "yaw_std": 0.0,
                "repeated_turns_count": 0,
                "movement_level": "Unavailable"
            },
            "gaze_summary": {
                "approx_camera_facing_pct": 0.0,
                "looking_away_pct": 0.0,
                "dominant_direction": "Unavailable",
                "disclaimer": "Landmark-based approximate gaze estimation. Does not infer thoughts or exact screen focus."
            },
            "posture_summary": {
                "upper_body_visible": False,
                "dominant_posture": "Unavailable",
                "average_shoulder_tilt_deg": None,
                "status_message": "Posture analysis unavailable because no camera frames were captured."
            },
            "visual_analysis_status": "unavailable",
            "coverage_summary": "0 frames captured (Camera inactive or inaccessible)",
            "observations": ["No visual frames were captured during this question."],
            "strengths": [],
            "suggestions": ["Ensure your webcam is connected and properly enabled."]
        }

    face_count = 0
    centered_count = 0
    multiple_face_count = 0

    yaws = []
    pitches = []
    rolls = []
    forward_count = 0
    camera_facing_count = 0

    centers_x = []
    centers_y = []

    consecutive_no_face = 0
    max_consecutive_no_face = 0

    gaze_directions = {}
    posture_votes = {}
    shoulder_tilts = []
    upper_body_visible_count = 0

    frame_analyses = []
    for frame in frames:
        res = analyze_frame(frame)
        frame_analyses.append(res)

        if res["face_detected"]:
            face_count += 1
            consecutive_no_face = 0
            if res["is_centered"]:
                centered_count += 1
            if res["multiple_faces"]:
                multiple_face_count += 1

            cx, cy = res["center_coords"]
            centers_x.append(cx)
            centers_y.append(cy)

            hp = res.get("head_pose", {})
            if hp.get("yaw") is not None:
                yaws.append(hp["yaw"])
                pitches.append(hp["pitch"])
                rolls.append(hp["roll"])
                if hp.get("is_forward", False):
                    forward_count += 1

            eg = res.get("eye_gaze", {})
            if eg.get("is_camera_facing", False):
                camera_facing_count += 1
            g_dir = eg.get("direction", "unavailable")
            gaze_directions[g_dir] = gaze_directions.get(g_dir, 0) + 1
        else:
            consecutive_no_face += 1
            if consecutive_no_face > max_consecutive_no_face:
                max_consecutive_no_face = consecutive_no_face

        p_data = res.get("posture", {})
        p_status = p_data.get("status", "unavailable")
        posture_votes[p_status] = posture_votes.get(p_status, 0) + 1
        if p_data.get("upper_body_visible", False):
            upper_body_visible_count += 1
            if p_data.get("tilt_deg") is not None:
                shoulder_tilts.append(p_data["tilt_deg"])

    # Compute Visibility and Presence metrics
    face_visibility_pct = round((face_count / total) * 100.0, 1)
    face_centering_pct = round((centered_count / max(1, face_count)) * 100.0, 1) if face_count > 0 else 0.0

    # Head-pose metrics
    avg_yaw = round(float(np.mean(yaws)), 1) if yaws else 0.0
    avg_pitch = round(float(np.mean(pitches)), 1) if pitches else 0.0
    avg_roll = round(float(np.mean(rolls)), 1) if rolls else 0.0
    yaw_std = round(float(np.std(yaws)), 1) if len(yaws) >= 2 else 0.0

    # Detect repeated left/right head oscillations
    repeated_turns = 0
    if len(yaws) >= 3:
        for i in range(1, len(yaws) - 1):
            if (yaws[i] - yaws[i - 1]) * (yaws[i + 1] - yaws[i]) < -100:
                repeated_turns += 1

    forward_facing_pct = round((forward_count / max(1, face_count)) * 100.0, 1) if face_count > 0 else 0.0
    camera_facing_pct = round((camera_facing_count / max(1, face_count)) * 100.0, 1) if face_count > 0 else 0.0

    # Classify natural head movement (Natural movement is expected)
    if face_count == 0:
        movement_level = "No face detected"
    elif yaw_std < 6.0:
        movement_level = "Low / Stable"
    elif yaw_std <= 16.0:
        movement_level = "Moderate / Natural"
    else:
        movement_level = "High / Active"

    # Posture metrics
    upper_body_visible = (upper_body_visible_count / total) >= 0.35 if total > 0 else False
    if upper_body_visible:
        dominant_posture = max(posture_votes, key=posture_votes.get) if posture_votes else "Upright"
        avg_tilt = round(float(np.mean(shoulder_tilts)), 1) if shoulder_tilts else None
        p_msg = f"Upper body visible. Posture: {dominant_posture} (Average shoulder tilt: {avg_tilt}°)."
    else:
        dominant_posture = "Unavailable"
        avg_tilt = None
        p_msg = "Posture analysis unavailable because the upper body was not sufficiently visible."

    # Determine analysis status
    if face_count == 0:
        status = "no_face_detected"
    elif total < 5:
        status = "insufficient_frames"
    else:
        status = "completed"

    # Human-readable observations & constructive suggestions
    observations = []
    strengths = []
    suggestions = []

    if face_visibility_pct >= 85.0:
        strengths.append(f"Consistent camera presence ({face_visibility_pct}% of the answer).")
    elif face_visibility_pct < 50.0:
        suggestions.append("Keep your face in front of the camera during your technical explanation.")

    if face_centering_pct >= 75.0:
        strengths.append(f"Well-centered within the camera frame ({face_centering_pct}%).")
    elif face_centering_pct < 40.0 and face_count > 0:
        suggestions.append("Adjust camera angle or seat position to stay centered in frame.")

    if camera_facing_pct >= 70.0:
        strengths.append(f"Maintained steady forward engagement ({camera_facing_pct}% camera-facing).")
    elif camera_facing_pct < 40.0 and face_count > 0:
        suggestions.append("Try addressing the camera more directly while explaining technical concepts.")

    if movement_level == "Moderate / Natural":
        observations.append("Natural, conversational head movement observed.")
    elif movement_level == "High / Active":
        observations.append("Frequent head turns or shifts observed during answer delivery.")
    elif movement_level == "Low / Stable":
        observations.append("Steady, composed head positioning observed.")

    if multiple_face_count > 0:
        observations.append(f"Multiple faces detected in {multiple_face_count} frame(s).")
        suggestions.append("Ensure you are alone in frame for realistic interview practice.")

    if not upper_body_visible:
        observations.append("Upper-body landmarks were not in camera frame (posture evaluation omitted).")
    else:
        observations.append(p_msg)

    coverage_summary = f"{face_count}/{total} frames analyzed ({face_visibility_pct}% coverage)"

    return {
        "question_id": question_id,
        "domain": domain,
        "skill": skill,
        "total_frames": total,
        "face_frames": face_count,
        "face_visibility_pct": face_visibility_pct,
        "face_centering_pct": face_centering_pct,
        "multiple_faces_detected": (multiple_face_count > 0),
        "multiple_face_occurrences": multiple_face_count,
        "max_consecutive_no_face_frames": max_consecutive_no_face,
        "head_pose_summary": {
            "forward_facing_pct": forward_facing_pct,
            "average_yaw": avg_yaw,
            "average_pitch": avg_pitch,
            "average_roll": avg_roll,
            "yaw_std": yaw_std,
            "repeated_turns_count": repeated_turns,
            "movement_level": movement_level
        },
        "gaze_summary": {
            "approx_camera_facing_pct": camera_facing_pct,
            "looking_away_pct": round(max(0.0, 100.0 - camera_facing_pct), 1),
            "dominant_direction": max(gaze_directions, key=gaze_directions.get) if gaze_directions else "direct",
            "disclaimer": "Landmark-based approximate gaze estimation. Does not infer thoughts or exact screen focus."
        },
        "posture_summary": {
            "upper_body_visible": upper_body_visible,
            "dominant_posture": dominant_posture,
            "average_shoulder_tilt_deg": avg_tilt,
            "status_message": p_msg
        },
        "visual_analysis_status": status,
        "coverage_summary": coverage_summary,
        "observations": observations,
        "strengths": strengths,
        "suggestions": suggestions
    }


# =============================================================================
# 6. OVERALL VISUAL PERFORMANCE AGGREGATION
# =============================================================================

def calculate_overall_visual_analysis(technical_video_results):
    """
    Computes weighted overall visual performance metrics across all technical questions.
    Uses actual valid frame counts to prevent distortion from questions with few frames.
    Distinguishes missing data from poor candidate performance.
    """
    if not technical_video_results or not isinstance(technical_video_results, dict):
        return {
            "overall_face_visibility_pct": 0.0,
            "overall_camera_facing_pct": 0.0,
            "overall_face_centering_pct": 0.0,
            "overall_head_movement": "Unavailable",
            "posture_availability": "Unavailable",
            "dominant_posture": "Unavailable",
            "multiple_face_events": 0,
            "total_questions_analyzed": 0,
            "questions_with_face_detected": 0,
            "questions_unavailable": 0,
            "overall_coverage_pct": 0.0,
            "key_observations": ["No visual analysis data recorded."],
            "improvement_suggestions": ["Enable webcam to receive visual engagement insights."],
            "disclaimer": "Webcam-based estimations reflect framing and landmark approximations. They do not measure personality, intelligence, or emotional state."
        }

    total_frames = 0
    total_face_frames = 0
    total_centered_frames = 0
    total_camera_facing_frames = 0
    total_multiple_face_events = 0

    questions_with_face = 0
    questions_unavailable = 0
    all_observations = []
    all_suggestions = []
    all_strengths = []

    posture_counts = {}
    upper_body_visible_q_count = 0

    for q_idx, q_res in technical_video_results.items():
        tf = q_res.get("total_frames", 0)
        ff = q_res.get("face_frames", 0)

        total_frames += tf
        total_face_frames += ff

        if ff > 0:
            questions_with_face += 1
            # Back-calculate frame counts from percentages
            c_pct = q_res.get("face_centering_pct", 0.0)
            total_centered_frames += int(round((c_pct / 100.0) * ff))

            g_pct = q_res.get("gaze_summary", {}).get("approx_camera_facing_pct", 0.0)
            total_camera_facing_frames += int(round((g_pct / 100.0) * ff))

        if q_res.get("visual_analysis_status") in ("unavailable", "no_face_detected"):
            questions_unavailable += 1

        total_multiple_face_events += q_res.get("multiple_face_occurrences", 0)

        p_info = q_res.get("posture_summary", {})
        if p_info.get("upper_body_visible", False):
            upper_body_visible_q_count += 1
            dom_p = p_info.get("dominant_posture", "Upright")
            posture_counts[dom_p] = posture_counts.get(dom_p, 0) + 1

        all_observations.extend(q_res.get("observations", []))
        all_suggestions.extend(q_res.get("suggestions", []))
        all_strengths.extend(q_res.get("strengths", []))

    tot_q = len(technical_video_results)

    # Weighted percentages
    overall_face_vis = round((total_face_frames / max(1, total_frames)) * 100.0, 1) if total_frames > 0 else 0.0
    overall_centering = round((total_centered_frames / max(1, total_face_frames)) * 100.0, 1) if total_face_frames > 0 else 0.0
    overall_camera_facing = round((total_camera_facing_frames / max(1, total_face_frames)) * 100.0, 1) if total_face_frames > 0 else 0.0

    # Overall posture
    if upper_body_visible_q_count > 0:
        dominant_posture = max(posture_counts, key=posture_counts.get)
        posture_avail = f"Available ({upper_body_visible_q_count}/{tot_q} questions)"
    else:
        dominant_posture = "Unavailable"
        posture_avail = "Unavailable (Upper body not sufficiently visible in camera view)"

    # Deduplicate observations and suggestions
    unique_obs = list(dict.fromkeys(all_observations))[:4]
    unique_sugg = list(dict.fromkeys(all_suggestions))[:3]
    unique_str = list(dict.fromkeys(all_strengths))[:3]

    if not unique_obs:
        unique_obs = ["Camera captured stable video frames across technical questions."]
    if not unique_sugg:
        unique_sugg = ["Continue maintaining direct, centered camera engagement."]

    return {
        "overall_face_visibility_pct": overall_face_vis,
        "overall_camera_facing_pct": overall_camera_facing,
        "overall_face_centering_pct": overall_centering,
        "overall_head_movement": "Moderate / Natural" if overall_face_vis >= 50.0 else "Low / Intermittent",
        "posture_availability": posture_avail,
        "dominant_posture": dominant_posture,
        "multiple_face_events": total_multiple_face_events,
        "total_questions_analyzed": tot_q,
        "questions_with_face_detected": questions_with_face,
        "questions_unavailable": questions_unavailable,
        "overall_coverage_pct": overall_face_vis,
        "key_observations": unique_obs,
        "strengths": unique_str,
        "improvement_suggestions": unique_sugg,
        "disclaimer": "Webcam-based estimations reflect framing and landmark approximations. They do not measure personality, intelligence, or emotional state."
    }


# =============================================================================
# 7. BACKWARD-COMPATIBLE AGGREGATION WRAPPER FOR MOCK HR INTERVIEW
# =============================================================================

def aggregate_video_analysis(frames):
    """
    Takes a list of RGB numpy arrays, analyzes each frame, and returns aggregated metrics.
    100% backward-compatible with Mock HR Interview and scoring.py while attaching Phase 3 data.
    """
    if not frames:
        return {
            "face_detected": False,
            "eye_contact": "poor",
            "movement": "high",
            "multiple_faces_detected": False,
            "face_presence_pct": 0.0,
            "face_position": "unavailable",
            "gaze_direction": "unavailable",
            "posture": "unavailable",
            "total_frames": 0,
            "face_frames": 0,
            "phase3_summary": analyze_technical_question_frames([])
        }

    q_analysis = analyze_technical_question_frames(frames)

    face_detected = (q_analysis["face_visibility_pct"] >= 50.0)
    eye_contact = "good" if q_analysis["gaze_summary"]["approx_camera_facing_pct"] >= 50.0 else "poor"
    movement = "high" if q_analysis["head_pose_summary"]["movement_level"] == "High / Active" else "low"

    return {
        # Core keys required by scoring.py and Mock HR Interview
        "face_detected": face_detected,
        "eye_contact": eye_contact,
        "movement": movement,
        "multiple_faces_detected": q_analysis["multiple_faces_detected"],
        "face_presence_pct": q_analysis["face_visibility_pct"],
        "face_position": "centered" if q_analysis["face_centering_pct"] >= 50.0 else "off-center",
        "gaze_direction": q_analysis["gaze_summary"]["dominant_direction"],
        "posture": q_analysis["posture_summary"]["dominant_posture"],
        "total_frames": q_analysis["total_frames"],
        "face_frames": q_analysis["face_frames"],
        # Attached Phase 3 comprehensive analysis
        "phase3_summary": q_analysis
    }
