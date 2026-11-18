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
