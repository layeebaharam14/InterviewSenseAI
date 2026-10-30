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

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Initialize MediaPipe Face Mesh for 3D landmarks and head pose estimation
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

# Initialize MediaPipe Pose for posture detection (shoulders)
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


def _estimate_head_pose(landmarks, image_shape):
    """
    Estimates head yaw, pitch, and roll in degrees using cv2.solvePnP.
    Returns (yaw, pitch, roll, gaze_direction) or (None, None, None, 'unavailable').
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
        dist_coeffs = np.zeros((4, 1))  # Assume minimal lens distortion

        success, rotation_vector, _ = cv2.solvePnP(
            _3D_MODEL_POINTS, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return None, None, None, "unavailable"

        rot_mat, _ = cv2.Rodrigues(rotation_vector)
        # Decompose projection matrix into Euler angles
        proj_matrix = np.hstack((rot_mat, np.zeros((3, 1))))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)
        pitch = float(euler_angles[0][0])
        yaw = float(euler_angles[1][0])
        roll = float(euler_angles[2][0])

        # Infer gaze / orientation
        if abs(yaw) < 16.0 and abs(pitch) < 16.0:
            gaze_dir = "direct"
        elif yaw <= -16.0:
            gaze_dir = "looking right"
        elif yaw >= 16.0:
            gaze_dir = "looking left"
        elif pitch <= -16.0:
            gaze_dir = "looking up"
        else:
            gaze_dir = "looking down"

        return yaw, pitch, roll, gaze_dir
    except Exception:
        return None, None, None, "unavailable"


def _estimate_posture(image):
    """
    Estimates candidate posture via MediaPipe Pose (shoulder alignment).
    Returns 'upright', 'tilted', or 'unavailable'.
    """
    if pose_tracker is None:
        return "unavailable"
    try:
        results = pose_tracker.process(image)
        if not results.pose_landmarks:
            return "unavailable"
        landmarks = results.pose_landmarks.landmark
        l_shoulder = landmarks[11]
        r_shoulder = landmarks[12]

        if getattr(l_shoulder, 'visibility', 0) > 0.5 and getattr(r_shoulder, 'visibility', 0) > 0.5:
            dy = r_shoulder.y - l_shoulder.y
            dx = r_shoulder.x - l_shoulder.x
            angle = abs(np.degrees(np.arctan2(dy, dx)))
            # Normalize angle relative to horizontal (180 or 0)
            tilt = min(angle, abs(180 - angle))
            return "upright" if tilt < 10.0 else "tilted"
        return "unavailable"
    except Exception:
        return "unavailable"


def analyze_frame(image):
    """
    Analyzes a single numpy array frame (RGB) to detect face, orientation, and posture.
    Returns backward-compatible dictionary for downstream consumers.
    """
    results = face_detection.process(image)

    face_detected = False
    eye_contact = "poor"
    movement = "high"
    multiple_faces = False
    face_position = "unavailable"
    head_pose = {"yaw": None, "pitch": None, "roll": None, "gaze": "unavailable"}
    posture = "unavailable"
    center_coords = (0.5, 0.5)

    if results.detections:
        face_detected = True
        num_detected = len(results.detections)
        multiple_faces = (num_detected > 1)

        # Primary face bounding box
        bboxC = results.detections[0].location_data.relative_bounding_box
        xc = bboxC.xmin + (bboxC.width / 2.0)
        yc = bboxC.ymin + (bboxC.height / 2.0)
        center_coords = (xc, yc)

        # Determine face position
        if 0.35 <= xc <= 0.65 and 0.25 <= yc <= 0.75:
            face_position = "centered"
        elif xc < 0.35:
            face_position = "off-center left"
        elif xc > 0.65:
            face_position = "off-center right"
        else:
            face_position = "off-center"

        # Determine default eye contact / movement from bounding box
        is_central = (0.25 < xc < 0.75 and 0.2 < yc < 0.8)
        eye_contact = "good" if is_central else "poor"
        movement = "low" if is_central else "high"

        # Face Mesh enhancement for head pose and precision gaze
        if face_mesh is not None:
            try:
                mesh_results = face_mesh.process(image)
                if mesh_results.multi_face_landmarks:
                    face_lms = mesh_results.multi_face_landmarks[0].landmark
                    yaw, pitch, roll, gaze_dir = _estimate_head_pose(face_lms, image.shape)
                    if gaze_dir != "unavailable":
                        head_pose = {"yaw": round(yaw, 1), "pitch": round(pitch, 1), "roll": round(roll, 1), "gaze": gaze_dir}
                        # Precision eye contact: must be facing camera directly and centered
                        if gaze_dir == "direct" and is_central:
                            eye_contact = "good"
                        else:
                            eye_contact = "poor"
            except Exception:
                pass

        # Posture check
        posture = _estimate_posture(image)

    return {
        "face_detected": face_detected,
        "eye_contact": eye_contact,
        "movement": movement,
        "multiple_faces": multiple_faces,
        "face_position": face_position,
        "head_pose": head_pose,
        "posture": posture,
        "center_coords": center_coords
    }


def aggregate_video_analysis(frames):
    """
    Takes a list of RGB numpy arrays, analyzes each frame, and returns aggregated metrics.
    100% backward-compatible with original schema while exposing enriched analytics.
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
            "face_frames": 0
        }

    total = len(frames)
    face_count = 0
    good_eye_contact = 0
    high_movement_count = 0
    multiple_faces_count = 0
    posture_votes = {"upright": 0, "tilted": 0, "unavailable": 0}
    centers_x = []
    centers_y = []
    gaze_votes = {}

    for frame in frames:
        res = analyze_frame(frame)
        if res["face_detected"]:
            face_count += 1
            if res["eye_contact"] == "good":
                good_eye_contact += 1
            if res["movement"] == "high":
                high_movement_count += 1
            if res.get("multiple_faces", False):
                multiple_faces_count += 1
            
            cx, cy = res.get("center_coords", (0.5, 0.5))
            centers_x.append(cx)
            centers_y.append(cy)

            gaze = res.get("head_pose", {}).get("gaze", "unavailable")
            gaze_votes[gaze] = gaze_votes.get(gaze, 0) + 1

        posture_status = res.get("posture", "unavailable")
        posture_votes[posture_status] = posture_votes.get(posture_status, 0) + 1

    # Aggregation rules
    face_presence_pct = round((face_count / total) * 100.0, 1) if total > 0 else 0.0
    face_detected = (face_presence_pct >= 50.0)

    # Standard deviation of face positions indicates stability / fidgeting
    if len(centers_x) >= 2:
        std_movement = (np.std(centers_x) + np.std(centers_y)) / 2.0
        movement = "high" if std_movement > 0.06 else "low"
    else:
        movement = "high" if (high_movement_count / max(1, face_count)) > 0.4 else "low"

    eye_contact = "good" if (good_eye_contact / max(1, face_count)) >= 0.55 else "poor"
    multiple_faces_detected = (multiple_faces_count > 0)

    # Dominant gaze and posture
    dominant_gaze = max(gaze_votes, key=gaze_votes.get) if gaze_votes else "unavailable"
    dominant_posture = max(posture_votes, key=posture_votes.get) if posture_votes else "unavailable"

    # Overall position
    if centers_x:
        avg_x = float(np.mean(centers_x))
        overall_pos = "centered" if 0.35 <= avg_x <= 0.65 else ("left" if avg_x < 0.35 else "right")
    else:
        overall_pos = "unavailable"

    return {
        # Core keys required by scoring.py and Mock HR Interview
        "face_detected": face_detected,
        "eye_contact": eye_contact,
        "movement": movement,
        # Extended multi-modal analytics for Technical & Real-time dashboards
        "face_presence_pct": face_presence_pct,
        "multiple_faces_detected": multiple_faces_detected,
        "face_position": overall_pos,
        "gaze_direction": dominant_gaze,
        "posture": dominant_posture,
        "total_frames": total,
        "face_frames": face_count
    }
