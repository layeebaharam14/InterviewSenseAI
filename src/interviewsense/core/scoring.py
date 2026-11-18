def calculate_scores(video_results_list, audio_results_list):
    """
    Calculates final scores based on the collected video and audio metrics across all questions.

    Changes vs original:
    - Skips audio penalties entirely when ``audio_available`` is False (hardware/SR failure).
      This prevents a microphone error from masking genuine behavioural performance.
    - Tracks how many questions have valid audio so the communication score is
      only penalised for answers where audio was actually obtainable.
    - Confidence and nervousness still reflect camera/video evidence when present.
    """
    total_questions = max(len(video_results_list), len(audio_results_list))
    if total_questions == 0:
        return {
            "confidence": 0,
            "nervousness": 0,
            "communication": 0,
            "audio_questions_evaluated": 0,
            "video_questions_evaluated": 0,
        }

    # Base scores
    confidence = 100
    nervousness = 0
    communication = 100

    audio_evaluated = 0   # questions with usable audio
    video_evaluated = 0   # questions where face was detectable at least once

    for i in range(total_questions):
        v_res = video_results_list[i] if i < len(video_results_list) else {}
        a_res = audio_results_list[i] if i < len(audio_results_list) else {}
        # -----------------------------------------------------------------
        # VIDEO / BEHAVIOURAL penalties
        # -----------------------------------------------------------------
        face_present = v_res.get("face_detected", False)

        if not face_present:
            # Camera was absent or face never detected — moderate penalty
            confidence -= 10
            nervousness += 10
        else:
            video_evaluated += 1
            if v_res.get("eye_contact") == "poor":
                confidence -= 5
                communication -= 5
            if v_res.get("movement") == "high":
                nervousness += 10
                confidence -= 5

        # -----------------------------------------------------------------
        # AUDIO / SPEECH penalties
        # Only applied when audio was actually available (audio_available=True).
        # If the flag is absent (legacy result), treat it as True for backward-compat.
        # -----------------------------------------------------------------
        audio_avail = a_res.get("audio_available", True)

        if not audio_avail:
            # Audio pipeline failed — do NOT penalise the candidate's scores.
            # Communication score simply cannot be evaluated for this question.
            pass
        else:
            audio_evaluated += 1

            if a_res.get("filler_words", 0) > 3:
                communication -= 5
                nervousness += 5

            if a_res.get("pauses", 0) > 2:
                communication -= 5
                confidence -= 5

            if not a_res.get("meaningful", True):
                # Candidate genuinely did not speak enough
                communication -= 20
                confidence -= 10

    # Normalize scores between 0 and 100
    confidence = max(0, min(100, confidence))
    nervousness = max(0, min(100, nervousness))
    communication = max(0, min(100, communication))

    return {
        "confidence": confidence,
        "nervousness": nervousness,
        "communication": communication,
        "audio_questions_evaluated": audio_evaluated,
        "video_questions_evaluated": video_evaluated,
    }
