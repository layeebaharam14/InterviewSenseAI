import re

def analyze_audio_behavior(text, duration):
    """
    Analyzes actual transcribed text to evaluate speech fluency, filler words, pauses, and speech rate.
    Maintains 100% backward-compatibility with scoring.py and Mock HR Interview.
    """
    if text is None:
        text = ""
        
    original_text = text
    text_lower = text.lower().strip()
    duration = max(1.0, float(duration))
    
    # Check for empty speech
    if not text_lower:
        return {
            "transcribed_text": "No speech detected.",
            "word_count": 0,
            "words_per_minute": 0.0,
            "speech_rate": "None",
            "filler_words": 0,
            "filler_details": {},
            "pauses": int(duration / 3),  # Assume high pauses if no speech
            "fluency_score": 0,
            "meaningful": False
        }
        
    words = re.findall(r'\b[\w\+\#\./\-]+\b', text_lower)
    word_count = len(words)
    
    # Common filler words (including technical hesitations)
    fillers = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally', 'sort of', 'kind of']
    
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
        
    # Meaningfulness check: at least 5 spoken words for 15s duration
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
        "meaningful": meaningful
    }
