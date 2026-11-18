import re

def analyze_audio_behavior(text, duration, audio_failed=False):
    """
    Analyzes actual transcribed text to evaluate speech fluency, filler words, pauses, and speech rate.
    Maintains 100% backward-compatibility with scoring.py and Mock HR Interview.

    Parameters
    ----------
    text : str
        The transcribed answer text. Pass "" or None when no speech was detected.
    duration : float
        Recording duration in seconds.
    audio_failed : bool, optional
        Set True when transcription could not be attempted (hardware error, network
        error, etc.). This distinguishes a hardware/SR failure from genuine silence,
        preventing unfair scoring penalties on the candidate.

    Returns
    -------
    dict
        Analysis results. The ``audio_available`` key is True when audio was
        captured and transcribed (or was silent), False when the audio pipeline
        itself failed before transcription could be attempted.
    """
    if text is None:
        text = ""

    original_text = text
    text_lower = text.lower().strip()
    duration = max(1.0, float(duration))

    # --- Case 1: Audio pipeline FAILED (hardware / network / SR error) --------
    # Return a neutral placeholder so calculate_scores() can skip this entry
    # rather than applying penalties the candidate doesn't deserve.
    if audio_failed:
        return {
            "transcribed_text": "",
            "word_count": 0,
            "words_per_minute": 0.0,
            "speech_rate": "Unavailable",
            "filler_words": 0,
            "filler_details": {},
            "pauses": 0,
            "fluency_score": 0,
            "meaningful": False,
            "audio_available": False,  # <-- sentinel for scoring.py
        }

    # --- Case 2: Genuine silence / no speech detected ------------------------
    if not text_lower:
        return {
            "transcribed_text": "No speech detected.",
            "word_count": 0,
            "words_per_minute": 0.0,
            "speech_rate": "None",
            "filler_words": 0,
            "filler_details": {},
            # FIX: was int(duration/3) which always triggered the pauses > 2 penalty.
            # A silent recording has 0 measured pauses (the whole slot was silent).
            "pauses": 0,
            "fluency_score": 0,
            "meaningful": False,
            "audio_available": True,  # audio WAS available, candidate just didn't speak
        }

    words = re.findall(r'\b[\w\+\#\./\-]+\b', text_lower)
    word_count = len(words)

    # Common filler words (including technical hesitations)
    fillers = ['um', 'uh', 'like', 'you know', 'basically', 'actually',
               'literally', 'sort of', 'kind of']

    filler_count = 0
    filler_details = {}
    for filler in fillers:
        cnt = len(re.findall(r'\b' + re.escape(filler) + r'\b', text_lower))
        if cnt > 0:
            filler_details[filler] = cnt
            filler_count += cnt

    # Calculate Words Per Minute
    wpm = round((word_count / duration) * 60, 1)

    if wpm < 60:
        speech_rate = "Slow"
    elif wpm <= 165:
        speech_rate = "Well-paced"
    else:
        speech_rate = "Fast"

    # Estimate pauses based on word count per second (avg normal conversational speech is ~2.2 words/sec)
    expected_words = duration * 2.2
    pauses = 0
    if word_count < (expected_words * 0.5):
        # Very slow speech, indicates long pauses
        pauses = int((expected_words - word_count) / 2.2 / 2)  # Rough estimation of heavy pauses

    # Meaningfulness check: at least 5 spoken words
    meaningful = word_count >= 5

    # Calculate fluency out of 100
    base_fluency = 100
    fluency_score = base_fluency - (filler_count * 5) - (pauses * 5)

    # Penalty for not speaking enough
    if not meaningful:
        fluency_score -= 30

    fluency_score = max(0, min(100, int(fluency_score)))

    return {
        "transcribed_text": original_text,
        "word_count": word_count,
        "words_per_minute": wpm,
        "speech_rate": speech_rate,
        "filler_words": filler_count,
        "filler_details": filler_details,
        "pauses": pauses,
        "fluency_score": fluency_score,
        "meaningful": meaningful,
        "audio_available": True,
    }
