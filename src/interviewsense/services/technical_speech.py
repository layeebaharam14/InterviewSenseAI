"""
technical_speech.py — InterviewSense AI
Phase 2: Reliable Voice Capture and Technical Speech Recognition Engine

Provides:
1. Context-aware technical terminology normalization across:
   - Programming languages (Python, Java, C, C++, JavaScript, TypeScript, etc.)
   - Programming keywords & syntax (OOP, async/await, lambda, null, pointer, etc.)
   - Data structures and algorithms (O(n), BFS, DFS, BST, HashMap, etc.)
   - Database terminology (SQL, NoSQL, ACID, BCNF, joins, indexing, etc.)
   - Operating systems (deadlock, mutex, semaphore, PCB, paging, etc.)
   - Computer networking (TCP/IP, UDP, DNS, OSI model, HTTP/HTTPS, etc.)
   - AI and Machine Learning (PyTorch, TensorFlow, CNN, backpropagation, etc.)
2. Safe 15-second audio capture with WAV disk caching for recovery and re-transcription.
3. Windows microphone error handling and PyAudio exception management.
4. Seamless fallback for empty, silent, or failed audio without data loss.
"""

import os
import re
import time
import tempfile
import speech_recognition as sr

# =============================================================================
# 1. TECHNICAL TERMINOLOGY NORMALIZATION RULES
# =============================================================================

# Universal cross-domain patterns (regex -> standardized technical term)
CORE_TECHNICAL_PATTERNS = [
    # Programming Languages & Stacks
    (r"\b(?:c\s*\+\s*\+|see\s+plus\s+plus|c\s+plus\s+plus)\b", "C++"),
    (r"\b(?:c\s*#|see\s+sharp|c\s+sharp)\b", "C#"),
    (r"\b(?:c\s+language)\b", "C language"),
    (r"\b(?:java\s+script)\b", "JavaScript"),
    (r"\b(?:type\s+script)\b", "TypeScript"),
    (r"\b(?:pie\s+thon|pie\s+than)\b", "Python"),
    (r"\b(?:python\s*ic)\b", "Pythonic"),
    (r"\b(?:golang|go\s+language)\b", "Go"),
    (r"\b(?:kot\s*lin)\b", "Kotlin"),
    (r"\b(?:post\s*gres|postgre\s*sql|post\s+grace)\b", "PostgreSQL"),
    (r"\b(?:mongo\s*db|mongo\s+d\s+b|mango\s+db)\b", "MongoDB"),
    (r"\b(?:no\s+sequel|no\s+sql)\b", "NoSQL"),
    (r"\b(?:sequel|s\s+q\s+l)\b", "SQL"),
    (r"\b(?:my\s+sequel|my\s+s\s+q\s+l)\b", "MySQL"),
    (r"\b(?:sqlite|s\s+q\s+l\s+lite)\b", "SQLite"),
    (r"\b(?:redis)\b", "Redis"),

    # Data Formats, Web & APIs
    (r"\b(?:jason|jay\s+son|j\s+son)\b", "JSON"),
    (r"\b(?:x\s+m\s+l)\b", "XML"),
    (r"\b(?:y\s+a\s+m\s+l|yam\s+el)\b", "YAML"),
    (r"\b(?:h\s+t\s+m\s+l)\b", "HTML"),
    (r"\b(?:c\s+s\s+s)\b", "CSS"),
    (r"\b(?:h\s+t\s+t\s+p)\b", "HTTP"),
    (r"\b(?:h\s+t\s+t\s+p\s+s)\b", "HTTPS"),
    (r"\b(?:u\s+r\s+l)\b", "URL"),
    (r"\b(?:u\s+r\s+i)\b", "URI"),
    (r"\b(?:rest\s+a\s+p\s+i|rest\s+api)\b", "REST API"),
    (r"\b(?:rest\s+full|restful\s+a\s+p\s+i)\b", "RESTful API"),
    (r"\b(?:graph\s+q\s+l|graphical\s+api)\b", "GraphQL"),
    (r"\b(?:git\s+hub)\b", "GitHub"),
    (r"\b(?:git\s+lab)\b", "GitLab"),
    (r"\b(?:c\s+i\s+c\s+d|c\s+i\s+slash\s+c\s+d)\b", "CI/CD"),
    (r"\b(?:a\s+p\s+i)\b", "API"),
    (r"\b(?:a\s+p\s+is)\b", "APIs"),
    (r"\b(?:s\s+d\s+k)\b", "SDK"),
    (r"\b(?:i\s+d\s+e)\b", "IDE"),
    (r"\b(?:u\s+i)\b", "UI"),
    (r"\b(?:u\s+x)\b", "UX"),
    (r"\b(?:cube\s*bernetes|k\s*eight\s*s|k8s)\b", "Kubernetes"),
    (r"\b(?:docker\s+container)\b", "Docker container"),

    # Big O & Complexity (Most specific patterns first)
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?(?:n\s+log\s+n|n\s+logn)\b", "O(n log n)"),
    (r"\b(?:o\s+of\s+n\s+log\s+n)\b", "O(n log n)"),
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?(?:n\s+squared|n\s*\^\s*2|n2)\b", "O(n^2)"),
    (r"\b(?:o\s+of\s+n\s+squared)\b", "O(n^2)"),
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?(?:two\s+to\s+the\s+n|2\s*\^\s*n)\b", "O(2^n)"),
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?(?:log\s+n|logarithmic)\b", "O(log n)"),
    (r"\b(?:o\s+of\s+log\s+n)\b", "O(log n)"),
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?(?:1|one)\b", "O(1)"),
    (r"\b(?:o\s+of\s+1|o\s+of\s+one)\b", "O(1)"),
    (r"\b(?:big\s+o|order\s+of)\s+(?:of\s+)?n\b", "O(n)"),
    (r"\b(?:o\s+of\s+n)\b", "O(n)"),

    # Computer Networks (Evaluated before short acronyms)
    (r"\b(?:o\s+s\s+i\s+model)\b", "OSI model"),
    (r"\b(?:t\s*c\s*p\s*/?\s*i\s*p|tcp\s+ip|t\s+c\s+p\s+i\s+p)\b", "TCP/IP"),
    (r"\b(?:u\s+d\s+p)\b", "UDP"),
    (r"\b(?:d\s+n\s+s)\b", "DNS"),
    (r"\b(?:d\s+h\s+c\s+p)\b", "DHCP"),
    (r"\b(?:i\s+p\s+v\s+4|ipv\s+4)\b", "IPv4"),
    (r"\b(?:i\s+p\s+v\s+6|ipv\s+6)\b", "IPv6"),
    (r"\b(?:i\s+p\s+address(?:es)?)\b", "IP address"),
    (r"\b(?:m\s+a\s+c\s+address)\b", "MAC address"),
    (r"\b(?:a\s+r\s+p)\b", "ARP"),
    (r"\b(?:s\s+s\s+l|t\s+l\s+s)\b", lambda m: m.group(0).upper().replace(" ", "")),
    (r"\b(?:s\s+y\s+n)\b", "SYN"),
    (r"\b(?:a\s+c\s+k)\b", "ACK"),

    # Data Structures & Algorithms
    (r"\b(?:b\s+f\s+s)\b", "BFS"),
    (r"\b(?:d\s+f\s+s)\b", "DFS"),
    (r"\b(?:b\s+s\s+t)\b", "BST"),
    (r"\b(?:a\s+v\s+l\s+tree)\b", "AVL tree"),
    (r"\b(?:link\s+list|linkedlist)\b", "linked list"),
    (r"\b(?:hash\s+map|hashmap)\b", "HashMap"),
    (r"\b(?:hash\s+table|hashtable)\b", "HashTable"),
    (r"\b(?:priority\s+q|priority\s+queue)\b", "priority queue"),
    (r"\b(?:l\s+i\s+f\s+o|lifo)\b", "LIFO"),
    (r"\b(?:f\s+i\s+f\s+o|fifo)\b", "FIFO"),
    (r"\b(?<!u\s)(?:d\s+p|dynamic\s+programming)\b", "dynamic programming"),

    # Architecture & Design
    (r"\b(?:o\s+o\s+p|o\s+o\s+p\s+s)\b", "OOP"),
    (r"\b(?:s\s+o\s+l\s+i\s+d)\b", "SOLID"),
    (r"\b(?:m\s+v\s+c)\b", "MVC"),
    (r"\b(?:d\s+r\s+y\s+principle)\b", "DRY principle"),

    # Database & SQL
    (r"\b(?:acid\s+properties|a\s+c\s+i\s+d)\b", "ACID properties"),
    (r"\b(?:r\s+d\s+b\s+m\s+s)\b", "RDBMS"),
    (r"\b(?:d\s+d\s+l)\b", "DDL"),
    (r"\b(?:d\s+m\s+l)\b", "DML"),
    (r"\b(?:d\s+c\s+l)\b", "DCL"),
    (r"\b(?:t\s+c\s+l)\b", "TCL"),
    (r"\b(?:b\s+c\s+n\s+f)\b", "BCNF"),
    (r"\b(?:1\s+n\s+f|first\s+normal\s+form)\b", "1NF"),
    (r"\b(?:2\s+n\s+f|second\s+normal\s+form)\b", "2NF"),
    (r"\b(?:3\s+n\s+f|third\s+normal\s+form)\b", "3NF"),
    (r"\b(?:primary\s+key)\b", "primary key"),
    (r"\b(?:foreign\s+key)\b", "foreign key"),
    (r"\b(?:inner\s+join|left\s+join|right\s+join|full\s+outer\s+join|cross\s+join)\b", lambda m: m.group(0).lower()),

    # Operating Systems
    (r"\b(?:c\s+p\s+u)\b", "CPU"),
    (r"\b(?:i\s+slash\s+o|i\s+o\s+bound|input\s+output)\b", "I/O"),
    (r"\b(?:dead\s+lock|deadlocks?)\b", "deadlock"),
    (r"\b(?:mew\s+tex|mewtex|mut\s+ex)\b", "mutex"),
    (r"\b(?:semi\s+four|sema\s+four|semaphores?)\b", "semaphore"),
    (r"\b(?:p\s+c\s+b|process\s+control\s+block)\b", "PCB"),
    (r"\b(?:t\s+c\s+b|thread\s+control\s+block)\b", "TCB"),
    (r"\b(?:l\s+r\s+u)\b", "LRU"),
    (r"\b(?:t\s+l\s+b)\b", "TLB"),
    (r"\b(?:r\s+a\s+m)\b", "RAM"),

    # AI & Machine Learning
    (r"\b(?:a\s+i)\b", "AI"),
    (r"\b(?:m\s+l)\b", "ML"),
    (r"\b(?:n\s+l\s+p)\b", "NLP"),
    (r"\b(?:c\s+n\s+n)\b", "CNN"),
    (r"\b(?:r\s+n\s+n)\b", "RNN"),
    (r"\b(?:l\s+s\s+t\s+m)\b", "LSTM"),
    (r"\b(?:g\s+a\s+n)\b", "GAN"),
    (r"\b(?:pie\s+torch)\b", "PyTorch"),
    (r"\b(?:tensor\s+flow)\b", "TensorFlow"),
    (r"\b(?:sci\s+kit\s+learn|sklearn)\b", "Scikit-learn"),
    (r"\b(?:num\s+pi|num\s+py|numpie)\b", "NumPy"),
    (r"\b(?:pan\s+das)\b", "Pandas"),
    (r"\b(?:k\s+means|k-means)\b", "K-Means"),
    (r"\b(?:k\s+n\s+n|k\s+nearest\s+neighbors?)\b", "KNN"),
    (r"\b(?:s\s+v\s+m)\b", "SVM"),
    (r"\b(?:back\s+prop(?:agation)?)\b", "backpropagation"),
]

# Domain-specific refinements
DOMAIN_TECHNICAL_PATTERNS = {
    "Python Programming": [
        (r"\b(?:dunder\s+init\s+method|dunder\s+init)\b", "dunder __init__ method"),
        (r"\b(?:init\s+method)\b", "__init__ method"),
        (r"\b(?:dunder|double\s+underscore)\b", "dunder"),
        (r"\b(?:lamb\s*da)\b", "lambda"),
        (r"\b(?:pip\s+install)\b", "pip install"),
        (r"\b(?:gil|global\s+interpreter\s+lock)\b", "GIL"),
        (r"\b(?:pep\s*8|pep\s+eight)\b", "PEP 8"),
        (r"\b(?:virtual\s+env)\b", "virtualenv"),
        (r"\b(?:args\s+and\s+kwargs|\*args\s+and\s+\*\*kwargs)\b", "*args and **kwargs"),
    ],
    "Java Programming": [
        (r"\b(?:j\s+v\s+m)\b", "JVM"),
        (r"\b(?:j\s+r\s+e)\b", "JRE"),
        (r"\b(?:j\s+d\s+k)\b", "JDK"),
        (r"\b(?:j\s+d\s+b\s+c)\b", "JDBC"),
        (r"\b(?:garbage\s+collector|g\s+c)\b", "garbage collector"),
        (r"\b(?:string\s+builder)\b", "StringBuilder"),
        (r"\b(?:array\s+list)\b", "ArrayList"),
    ],
    "C Programming": [
        (r"\b(?:mal\s*loc)\b", "malloc"),
        (r"\b(?:cal\s*loc)\b", "calloc"),
        (r"\b(?:re\s*alloc)\b", "realloc"),
        (r"\b(?:free\s+function|free\(\))\b", "free()"),
        (r"\b(?:null\s+pointer)\b", "NULL pointer"),
        (r"\b(?:seg\s*fault|segmentation\s+fault)\b", "segmentation fault"),
    ],
    "C++ Programming": [
        (r"\b(?:s\s+t\s+l)\b", "STL"),
        (r"\b(?:std\s+vector)\b", "std::vector"),
        (r"\b(?:cout|c\s+out)\b", "std::cout"),
        (r"\b(?:cin|c\s+in)\b", "std::cin"),
        (r"\b(?:virtual\s+destructor)\b", "virtual destructor"),
    ],
    "Web Development": [
        (r"\b(?:dom\s+tree|d\s+o\s+m)\b", "DOM"),
        (r"\b(?:css\s+grid|flex\s*box)\b", lambda m: m.group(0).lower()),
        (r"\b(?:react\s+js|reactjs)\b", "React"),
        (r"\b(?:node\s+js|nodejs)\b", "Node.js"),
        (r"\b(?:npm\s+package)\b", "npm package"),
        (r"\b(?:cross\s+origin|cors|c\s+o\s+r\s+s)\b", "CORS"),
    ],
    "Database Management Systems (DBMS)": [
        (r"\b(?:atomicity|consistency|isolation|durability)\b", lambda m: m.group(0).capitalize()),
        (r"\b(?:er\s+diagram|e\s+r\s+diagram)\b", "ER diagram"),
        (r"\b(?:b\s+tree|b\s+plus\s+tree)\b", "B-tree / B+ tree"),
    ],
    "SQL": [
        (r"\b(?:group\s+by)\b", "GROUP BY"),
        (r"\b(?:order\s+by)\b", "ORDER BY"),
        (r"\b(?:having\s+clause)\b", "HAVING clause"),
        (r"\b(?:select\s+query)\b", "SELECT query"),
    ],
    "Operating Systems": [
        (r"\b(?:round\s+robin)\b", "Round Robin"),
        (r"\b(?:first\s+come\s+first\s+served|f\s+c\s+f\s+s)\b", "FCFS"),
        (r"\b(?:shortest\s+job\s+first|s\s+j\s+f)\b", "SJF"),
        (r"\b(?:bankers?\s+algorithm)\b", "Banker's algorithm"),
    ],
    "Computer Networks": [
        (r"\b(?:three\s+way\s+handshake)\b", "three-way handshake"),
        (r"\b(?:c\s+s\s+m\s+a\s+slash\s+c\s+d)\b", "CSMA/CD"),
        (r"\b(?:subnet\s+mask)\b", "subnet mask"),
        (r"\b(?:default\s+gateway)\b", "default gateway"),
    ],
    "Artificial Intelligence and Machine Learning": [
        (r"\b(?:over\s*fitting)\b", "overfitting"),
        (r"\b(?:under\s*fitting)\b", "underfitting"),
        (r"\b(?:gradient\s+descent)\b", "gradient descent"),
        (r"\b(?:loss\s+function|cost\s+function)\b", "loss function"),
        (r"\b(?:epoch|epochs)\b", "epoch"),
        (r"\b(?:learning\s+rate)\b", "learning rate"),
    ],
}

def normalize_technical_terms(text: str, domain: str = None, skills: list = None) -> str:
    """
    Normalizes phonetic and misrecognized speech text into accurate technical terminology.
    Does NOT invent words or hallucinate context; strictly applies equivalence transformations.
    """
    if not text or not isinstance(text, str):
        return ""
    
    normalized = text

    # 1. Apply core technical patterns
    for pattern, replacement in CORE_TECHNICAL_PATTERNS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # 2. Apply domain-specific patterns if domain matches
    if domain and domain in DOMAIN_TECHNICAL_PATTERNS:
        for pattern, replacement in DOMAIN_TECHNICAL_PATTERNS[domain]:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Clean up excess whitespace
    normalized = re.sub(r"[ \t]+", " ", normalized).strip()
    return normalized

# =============================================================================
# 2. AUDIO FILE RECOVERY & CACHING
# =============================================================================

def get_temp_audio_dir() -> str:
    """Returns the dedicated directory for temporary technical interview audio."""
    temp_dir = os.path.join(tempfile.gettempdir(), "interviewsense_audio")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def get_temp_audio_path(session_id: str, question_index: int) -> str:
    """Generates an isolated temporary audio file path for a question recording."""
    d = get_temp_audio_dir()
    clean_sid = re.sub(r"[^a-zA-Z0-9_-]", "", str(session_id))[:16]
    return os.path.join(d, f"audio_{clean_sid}_q{question_index}.wav")

def cleanup_temp_audio(session_id: str = None):
    """
    Safely cleans up temporary audio files.
    If session_id is provided, deletes files for that session.
    Also purges any orphaned audio files older than 2 hours.
    """
    d = get_temp_audio_dir()
    if not os.path.exists(d):
        return
    now = time.time()
    clean_sid = re.sub(r"[^a-zA-Z0-9_-]", "", str(session_id))[:16] if session_id else None
    try:
        for fname in os.listdir(d):
            fpath = os.path.join(d, fname)
            if not os.path.isfile(fpath):
                continue
            should_remove = False
            if clean_sid and clean_sid in fname:
                should_remove = True
            elif now - os.path.getmtime(fpath) > 7200:
                should_remove = True
            if should_remove:
                try:
                    os.remove(fpath)
                except Exception:
                    pass
    except Exception:
        pass

# =============================================================================
# 3. RELIABLE AUDIO CAPTURE AND TRANSCRIPTION PIPELINE
# =============================================================================

def record_and_transcribe_audio(
    duration: int = 15,
    result_container: list = None,
    domain: str = None,
    skills: list = None,
    audio_file_path: str = None
):
    """
    Records audio for exactly `duration` seconds and transcribes it with technical normalization.
    Saves the 16-bit PCM WAV to `audio_file_path` for candidate recovery and re-transcription.
    Pushes results into `result_container`.
    """
    if result_container is None:
        result_container = []

    r = sr.Recognizer()
    # Tune recognizer parameters for technical speech
    r.dynamic_energy_threshold = True
    r.pause_threshold = 2.0

    try:
        with sr.Microphone() as source:
            # Short ambient noise calibration to preserve candidate's opening speech
            try:
                r.adjust_for_ambient_noise(source, duration=0.25)
            except Exception:
                pass

            # Record strictly for the specified duration
            audio_data = r.record(source, duration=duration)

            # Persist WAV file for candidate recovery
            if audio_file_path:
                try:
                    with open(audio_file_path, "wb") as f:
                        f.write(audio_data.get_wav_data())
                except Exception as err:
                    print(f"Warning: Could not save temp audio file: {err}")

            # Recognize and normalize speech
            try:
                raw_text = r.recognize_google(audio_data)
                if raw_text and raw_text.strip():
                    cleaned_text = normalize_technical_terms(raw_text.strip(), domain=domain, skills=skills)
                    result_container.append(cleaned_text)
                else:
                    result_container.append("ERROR: No speech detected.")
            except sr.UnknownValueError:
                result_container.append("ERROR: Speech Recognition could not understand the audio (No speech detected).")
            except sr.RequestError as e:
                result_container.append(f"ERROR: Speech recognition service unavailable ({e}). Please check your internet connection.")
    except (OSError, IOError) as e:
        result_container.append(f"ERROR: Microphone access error ({e}). Please verify microphone permissions.")
    except Exception as e:
        result_container.append(f"ERROR: Audio capture failure ({e}).")

    return result_container

def transcribe_audio_file(audio_path: str, domain: str = None, skills: list = None):
    """
    Re-transcribes an existing WAV audio file without recording from the microphone again.
    Returns: (success: bool, transcript_or_error: str)
    """
    if not audio_path or not os.path.exists(audio_path):
        return False, "Temporary audio recording file could not be found."

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)

        raw_text = r.recognize_google(audio_data)
        if not raw_text or not raw_text.strip():
            return False, "No speech detected in the audio recording."

        cleaned_text = normalize_technical_terms(raw_text.strip(), domain=domain, skills=skills)
        return True, cleaned_text
    except sr.UnknownValueError:
        return False, "Could not understand the audio recording (No clear speech detected)."
    except sr.RequestError as e:
        return False, f"Speech recognition service unavailable ({e}). Please check your internet connection."
    except Exception as e:
        return False, f"Error processing audio recording ({e})."
