from datetime import datetime
from src.interviewsense.core.scoring import calculate_scores


def generate_feedback(scores):
    """
    Generates positive, improvement, and negative feedback points, along with a final verdict.

    Changes vs original:
    - Accounts for audio_questions_evaluated / video_questions_evaluated so feedback
      reflects partial data honestly.
    - Feedback messages are specific to what was actually observed rather than three
      hardcoded generic strings.
    - Critical Issues section only fires when genuinely warranted by the data.
    - Overall score excludes unavailable dimensions rather than treating them as zero.
    """
    conf = scores["confidence"]
    nerv = scores["nervousness"]
    comm = scores["communication"]

    # Number of questions with reliable audio / video data
    audio_q = scores.get("audio_questions_evaluated", -1)   # -1 = unknown (legacy)
    video_q = scores.get("video_questions_evaluated", -1)

    positive = []
    improvement = []
    negative = []

    # ------------------------------------------------------------------
    # Confidence feedback
    # ------------------------------------------------------------------
    if conf >= 80:
        positive.append("You appeared confident and composed throughout the interview.")
    elif conf >= 60:
        improvement.append(
            "Your confidence level was moderate. Try to maintain a steady forward gaze "
            "and avoid frequent head turns while speaking."
        )
    elif conf >= 40:
        improvement.append(
            "Confidence appeared lower than ideal. Practising in front of a camera "
            "and working on eye contact can help project stronger self-assurance."
        )
    else:
        negative.append(
            "Low confidence indicators observed (limited face visibility or frequent "
            "avoidance of forward gaze). Consider dedicated interview rehearsal."
        )

    # ------------------------------------------------------------------
    # Nervousness feedback
    # ------------------------------------------------------------------
    if nerv <= 20:
        positive.append("You displayed very few observable nervousness indicators — calm and steady delivery.")
    elif nerv <= 45:
        improvement.append(
            "Some observable nervousness indicators were detected (e.g., frequent movement or "
            "head turns). Practising deep breathing before answers can help."
        )
    else:
        negative.append(
            "High observable nervousness indicators were recorded. Focus on staying physically "
            "still and speaking at a measured pace."
        )

    # ------------------------------------------------------------------
    # Communication feedback — be explicit when audio was unavailable
    # ------------------------------------------------------------------
    if audio_q == 0:
        # No audio was evaluable at all
        improvement.append(
            "Communication could not be evaluated — no audio was successfully captured. "
            "Check microphone permissions and connectivity before retaking."
        )
    elif audio_q > 0 and comm >= 80:
        positive.append(
            f"Good communication quality: clear speech rate and low filler word usage "
            f"across {audio_q} evaluated answer(s)."
        )
    elif audio_q > 0 and comm >= 55:
        improvement.append(
            "Communication was acceptable but can be improved. Aim to reduce filler words "
            "(e.g., 'um', 'uh', 'basically') and speak at a measured pace."
        )
    elif audio_q > 0 and comm < 55:
        negative.append(
            "Communication showed notable weaknesses: low word count, frequent pauses, "
            "or unclear delivery in several answers."
        )
    else:
        # Legacy path: audio_q unknown, fall back to score-only rules
        if comm >= 80:
            positive.append("Good communication clarity and fluency.")
        elif comm >= 50:
            improvement.append("Try reducing pauses and filler words.")
        else:
            negative.append("Too many pauses and filler words observed.")

    # ------------------------------------------------------------------
    # Ensure at least one entry in each section
    # ------------------------------------------------------------------
    if not positive:
        positive.append("Interview completed — keep practising to build on your performance.")
    if not improvement:
        improvement.append("Continue refining your answers with structured examples (STAR method).")

    # ------------------------------------------------------------------
    # Overall score calculation
    # Only include communication in the average when audio was evaluable.
    # ------------------------------------------------------------------
    if audio_q == 0:
        # Communication genuinely unknown — base verdict on confidence + nervousness only
        avg_score = (conf + (100 - nerv)) / 2
        score_note = "Communication dimension excluded (audio unavailable)."
    else:
        avg_score = (conf + (100 - nerv) + comm) / 3
        score_note = ""

    if avg_score >= 80:
        verdict = "Ready for Interview"
        verdict_class = "verdict-Ready"
    elif avg_score >= 55:
        verdict = "Needs Improvement"
        verdict_class = "verdict-Improve"
    else:
        verdict = "Not Ready"
        verdict_class = "verdict-NotReady"

    return {
        "positive": positive,
        "improvement": improvement,
        "negative": negative,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "overall_score": int(avg_score),
        "score_note": score_note,
    }


def evaluate_mock_question(question_text: str, video_res: dict = None, audio_res: dict = None) -> dict:
    """
    Evaluates candidate performance on an individual Mock HR interview question.
    Extracts transparent behavioral and speech signals, candidate transcript,
    and returns concrete evidence-based observations and practical improvements.
    """
    if video_res is None:
        video_res = {}
    if audio_res is None:
        audio_res = {}

    audio_avail = audio_res.get("audio_available", True)
    meaningful = audio_res.get("meaningful", True)
    raw_text = audio_res.get("transcribed_text", "")
    wpm = audio_res.get("words_per_minute", 0.0)
    words = audio_res.get("word_count", 0)
    rate = audio_res.get("speech_rate", "—")
    fillers = audio_res.get("filler_words", 0)
    filler_details = audio_res.get("filler_details", {})
    pauses = audio_res.get("pauses", 0)
    fluency = audio_res.get("fluency_score", 0)

    face_detected = video_res.get("face_detected", False)
    eye_contact = video_res.get("eye_contact", "unavailable")
    movement = video_res.get("movement", "unavailable")
    face_pos = video_res.get("face_position", "unavailable")
    gaze_dir = video_res.get("gaze_direction", "unavailable")
    posture = video_res.get("posture", "unavailable")
    face_presence_pct = video_res.get("face_presence_pct", 0.0)

    # Determine audio status
    if not audio_avail:
        audio_status = "unavailable"
        transcript_display = "[Audio Unavailable — hardware or speech recognition service error]"
    elif not raw_text.strip() or raw_text == "No speech detected." or (not meaningful and words == 0):
        audio_status = "silent"
        transcript_display = "[No speech detected — silence recorded]"
    else:
        audio_status = "transcribed"
        transcript_display = raw_text

    # Determine video status
    if face_detected:
        video_status = "detected"
    elif face_presence_pct > 0:
        video_status = "intermittent"
    else:
        video_status = "unavailable"

    what_went_well = []
    what_to_improve = []

    # Positives - Audio
    if audio_status == "transcribed":
        if rate == "Well-paced":
            what_went_well.append(f"Spoke at a well-paced speech rate ({wpm} WPM).")
        elif rate in ("Slow", "Fast") and words >= 10:
            what_went_well.append(f"Substantive answer provided ({words} words).")
        if fillers <= 1:
            what_went_well.append("Disciplined delivery with minimal or zero filler words.")
        elif fillers <= 3:
            what_went_well.append(f"Controlled filler word usage ({fillers} detected).")
        if pauses <= 1:
            what_went_well.append("Fluid cadence with minimal hesitation or long pauses.")
        if fluency >= 80:
            what_went_well.append(f"Strong verbal fluency ({fluency}/100) reflecting coherent expression.")

    # Positives - Video
    if video_status == "detected":
        if eye_contact == "good":
            what_went_well.append("Maintained consistent forward eye contact with the camera.")
        if movement == "low":
            what_went_well.append("Demonstrated composed posture and steady physical presence.")
        if face_pos == "centered":
            what_went_well.append("Framed centrally in the camera field of view.")
        if posture in ("Upright", "Neutral"):
            what_went_well.append(f"Maintained an upright, professional posture ({posture}).")

    if not what_went_well:
        if video_status == "detected":
            what_went_well.append("Candidate was present and engaged during the question window.")
        elif audio_status == "transcribed":
            what_went_well.append("Response was recorded and transcribed successfully.")
        else:
            what_went_well.append("Question completed during the interview session.")

    # Improvements - Audio
    if audio_status == "unavailable":
        what_to_improve.append("Audio unavailable: verify microphone hardware, permissions, and network connectivity.")
    elif audio_status == "silent":
        what_to_improve.append("No speech recorded: ensure microphone is not muted and speak clearly into the receiver.")
    else:
        if fillers > 2:
            filler_items = [f"'{f}' ({c})" for f, c in filler_details.items() if c > 0]
            filler_text = f" ({', '.join(filler_items[:3])})" if filler_items else ""
            what_to_improve.append(f"Reduce filler words: {fillers} detected{filler_text}. Practice pausing silently instead of using verbal fillers.")
        if rate == "Fast":
            what_to_improve.append(f"Fast delivery pace ({wpm} WPM). Slow down slightly to give your points greater impact.")
        elif rate == "Slow" and words > 0:
            what_to_improve.append(f"Slow delivery pace ({wpm} WPM). Aim for a more energetic, conversational rhythm (110-150 WPM).")
        if pauses > 2:
            what_to_improve.append(f"Estimated {pauses} noticeable pauses. Structure answers mentally before speaking to maintain steady flow.")
        if not meaningful:
            what_to_improve.append("Response was very brief (under 5 words). Elaborate using concrete examples.")

    # Improvements - Video
    if video_status == "unavailable":
        what_to_improve.append("Face was not detected: ensure your camera is enabled, lens is uncovered, and face is well-lit.")
    elif video_status == "intermittent":
        what_to_improve.append("Face presence was intermittent: stay within the camera frame during the entire answer.")
    else:
        if eye_contact == "poor":
            what_to_improve.append("Frequent gaze deflection: practice looking directly at the camera to establish engagement.")
        if movement == "high":
            what_to_improve.append("Noticeable movement or head fidgeting: maintain steady, relaxed composure.")
        if face_pos == "off-center":
            what_to_improve.append("Face was off-center: reposition your webcam or chair so you are framed in the center.")

    if not what_to_improve:
        what_to_improve.append("Strong overall answer — continue refining delivery using structured examples (STAR method).")

    return {
        "question": question_text,
        "transcript": transcript_display,
        "raw_text": raw_text,
        "audio_status": audio_status,
        "video_status": video_status,
        "audio_available": audio_avail,
        "meaningful": meaningful,
        "word_count": words,
        "words_per_minute": wpm,
        "speech_rate": rate,
        "filler_words": fillers,
        "filler_details": filler_details,
        "pauses": pauses,
        "fluency_score": fluency,
        "face_detected": face_detected,
        "eye_contact": eye_contact,
        "movement": movement,
        "face_presence_pct": face_presence_pct,
        "face_position": face_pos,
        "gaze_direction": gaze_dir,
        "posture": posture,
        "what_went_well": what_went_well,
        "what_to_improve": what_to_improve,
    }


def generate_mock_interview_summary(
    questions: list,
    video_results: list,
    audio_results: list,
    scores: dict = None,
    feedback: dict = None,
    candidate_name: str = ""
) -> dict:
    """
    Assembles a comprehensive, structured evaluation dictionary for the entire Mock HR interview.
    Used consistently by both the Streamlit UI dashboard and the multi-page PDF generator.
    """
    if scores is None:
        scores = calculate_scores(video_results, audio_results)
    if feedback is None:
        feedback = generate_feedback(scores)

    total_q = len(questions)
    audio_q = scores.get("audio_questions_evaluated", 0)
    video_q = scores.get("video_questions_evaluated", 0)

    # Evaluate each individual question
    question_evals = []
    for i in range(total_q):
        q_text = questions[i]
        v_res = video_results[i] if i < len(video_results) else {}
        a_res = audio_results[i] if i < len(audio_results) else {}
        question_evals.append(evaluate_mock_question(q_text, v_res, a_res))

    # Coverage calculations
    audio_coverage_pct = round((audio_q / total_q) * 100, 1) if total_q > 0 else 0.0
    video_coverage_pct = round((video_q / total_q) * 100, 1) if total_q > 0 else 0.0

    if total_q == 0:
        coverage_status = "No Questions Recorded"
    elif audio_q == total_q and video_q == total_q:
        coverage_status = "Full (100% Audio & Video)"
    elif audio_q == 0 and video_q > 0:
        coverage_status = "Visual Only (Audio Unavailable)"
    elif video_q == 0 and audio_q > 0:
        coverage_status = "Audio Only (Camera Unavailable)"
    elif audio_q == 0 and video_q == 0:
        coverage_status = "Incomplete (Hardware Unavailable)"
    else:
        coverage_status = f"Partial ({video_q}/{total_q} Video, {audio_q}/{total_q} Audio)"

    limitations = [
        "Webcam and microphone measurements approximate observable behavioural cues (framing, gaze orientation, speech pace).",
        "This evaluation does not claim to diagnose psychology, personality, intelligence, or internal emotional states.",
        "Scores reflect simulated practice conditions and should be used as guidance for interview preparation."
    ]
    if total_q > 0 and audio_q < total_q:
        limitations.append(
            f"Audio capture was unavailable on {total_q - audio_q} of {total_q} question(s); "
            "communication evaluation was excluded or adjusted accordingly."
        )
    if total_q > 0 and video_q < total_q:
        limitations.append(
            f"Face presence was absent or intermittent on {total_q - video_q} of {total_q} question(s)."
        )

    return {
        "candidate_name": candidate_name or "Candidate",
        "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M %p"),
        "total_questions": total_q,
        "audio_questions_evaluated": audio_q,
        "video_questions_evaluated": video_q,
        "audio_coverage_pct": audio_coverage_pct,
        "video_coverage_pct": video_coverage_pct,
        "coverage_status": coverage_status,
        "overall_score": feedback["overall_score"],
        "verdict": feedback["verdict"],
        "verdict_class": feedback["verdict_class"],
        "score_note": feedback.get("score_note", ""),
        "confidence_score": scores["confidence"],
        "nervousness_score": scores["nervousness"],
        "communication_score": scores["communication"] if audio_q > 0 else None,
        "scores": scores,
        "feedback": feedback,
        "strengths": feedback["positive"],
        "improvements": feedback["improvement"],
        "critical_issues": feedback["negative"],
        "question_evaluations": question_evals,
        "limitations": limitations,
    }
