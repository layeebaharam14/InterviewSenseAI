import streamlit as st
import streamlit.components.v1 as components
import cv2
import time
import random
import threading
import speech_recognition as sr

# Import internal modules
from utils import apply_css, speak_question
from video_analysis import aggregate_video_analysis
from audio_analysis import analyze_audio_behavior
from scoring import calculate_scores
from insights import generate_feedback
from technical_questions import generate_technical_questions
from technical_evaluation import evaluate_technical_interview, evaluate_technical_answer, classify_performance

# Application Configuration
st.set_page_config(page_title="InterviewSense AI", layout="centered")

QUESTION_POOL = [
    "What are your strengths?",
    "What is your biggest weakness?",
    "Describe a challenge you faced and how you handled it.",
    "Tell me about a time you worked in a team.",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?",
    "Tell me about a failure and what you learned.",
    "How do you handle pressure or deadlines?",
    "Describe a leadership experience.",
    "Why are you interested in this role?"
]

def get_question_duration(question):
    q = question.lower()
    if "tell me about yourself" in q:
        return 30
    if "challenge" in q or "situation" in q:
        return 25
    if "strength" in q or "weakness" in q:
        return 20
    return 15

def get_camera():
    # Try cameras 0 (default), 1, 2 with CAP_DSHOW for Windows compatibility
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Using camera: {index} with CAP_DSHOW")
                return cap
        cap.release()

    # Fallback without CAP_DSHOW
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Using camera: {index} without CAP_DSHOW")
                return cap
        cap.release()

    return None

def record_and_transcribe(duration, result_container):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            # Slightly longer calibration for better accuracy
            r.adjust_for_ambient_noise(source, duration=1.0)
            # Record exactly for the duration
            audio_data = r.record(source, duration=duration)
            try:
                text = r.recognize_google(audio_data)
                result_container.append(text)
            except sr.UnknownValueError:
                result_container.append("ERROR: Speech Recognition could not understand the audio (No speech detected).")
            except sr.RequestError as e:
                result_container.append(f"ERROR: Google Speech API unavailable ({e}).")
    except Exception as e:
          result_container.append(f"ERROR: Microphone error ({e}).")

def record_technical_voice_answer(duration=15):
    """Records audio from microphone and returns (success: bool, text_or_error: str) for Technical Interview."""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            audio_data = r.record(source, duration=duration)
            try:
                text = r.recognize_google(audio_data)
                if not text or not text.strip():
                    return False, "No speech detected. Please speak closer to your microphone."
                return True, text.strip()
            except sr.UnknownValueError:
                return False, "Could not understand audio. Please speak clearly into your microphone."
            except sr.RequestError as e:
                return False, f"Speech recognition service unavailable ({e}). Please check your internet connection or type your answer."
    except Exception as e:
        return False, f"Microphone error: {e}. Please ensure your microphone is connected and permissions are granted."

def save_current_technical_answer(curr_idx, method=None):
    """Persists the current question's answer from session state into technical_answers."""
    if 'technical_questions' not in st.session_state or not st.session_state.technical_questions:
        return
    if curr_idx < 0 or curr_idx >= len(st.session_state.technical_questions):
        return
    curr_q_data = st.session_state.technical_questions[curr_idx]
    ans_text = st.session_state.get(f"tech_ans_input_{curr_idx}", "").strip()
    
    existing_entry = st.session_state.technical_answers.get(curr_idx, {})
    if method is None:
        method = existing_entry.get("answer_method", "text") if ans_text else "text"
        
    st.session_state.technical_answers[curr_idx] = {
        "question_id": curr_idx + 1,
        "question": curr_q_data.get("question", ""),
        "domain": curr_q_data.get("domain", st.session_state.technical_domain),
        "skill": curr_q_data.get("skill", "General"),
        "difficulty": curr_q_data.get("difficulty", st.session_state.technical_difficulty),
        "question_type": curr_q_data.get("question_type", "Conceptual"),
        "answer_text": ans_text,
        "answer_method": method
    }

def init_session_state():
    """Initialize necessary session state variables."""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'Home'
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = []
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'video_results' not in st.session_state:
        st.session_state.video_results = []
    if 'audio_results' not in st.session_state:
        st.session_state.audio_results = []
    if 'question_spoken' not in st.session_state:
        st.session_state.question_spoken = False
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'frames' not in st.session_state:
        st.session_state.frames = []
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'hardware_verified' not in st.session_state:
        st.session_state.hardware_verified = False
    if 'last_audio_error' not in st.session_state:
        st.session_state.last_audio_error = None
    if 'technical_domain' not in st.session_state:
        st.session_state.technical_domain = "Python Programming"
    if 'technical_skills' not in st.session_state:
        st.session_state.technical_skills = []
    if 'technical_difficulty' not in st.session_state:
        st.session_state.technical_difficulty = "Intermediate"
    if 'technical_num_questions' not in st.session_state:
        st.session_state.technical_num_questions = "5 Questions"
    if 'previous_technical_domain' not in st.session_state:
        st.session_state.previous_technical_domain = "Python Programming"
    if 'technical_questions' not in st.session_state:
        st.session_state.technical_questions = []
    if 'technical_question_index' not in st.session_state:
        st.session_state.technical_question_index = 0
    if 'technical_answers' not in st.session_state:
        st.session_state.technical_answers = {}
    if 'technical_interview_completed' not in st.session_state:
        st.session_state.technical_interview_completed = False
    if 'technical_interview_submitted' not in st.session_state:
        st.session_state.technical_interview_submitted = False
    if 'confirm_end_technical' not in st.session_state:
        st.session_state.confirm_end_technical = False
    if 'confirm_submit_technical' not in st.session_state:
        st.session_state.confirm_submit_technical = False
    if 'technical_evaluation_results' not in st.session_state:
        st.session_state.technical_evaluation_results = None
    if 'technical_overall_score' not in st.session_state:
        st.session_state.technical_overall_score = 0
    if 'technical_performance_level' not in st.session_state:
        st.session_state.technical_performance_level = "Needs Improvement"
    if 'technical_evaluation_completed' not in st.session_state:
        st.session_state.technical_evaluation_completed = False

def render_landing_page():
    # Inject Top Navigation Bar using Streamlit Radio
    st.radio(
        "Navigation",
        ["Home", "About", "Features", "Guidelines"],
        horizontal=True,
        label_visibility="collapsed",
        key="current_tab"
    )
    
    if st.session_state.current_tab == "Home":
        # HOME SECTION
        st.markdown("""<div id="home-bg-injector">
<style>
/* Ensure containers stay transparent over the global background image */
.stApp, [data-testid="stAppViewContainer"] {
    color: white !important;
}
/* Force the white card container to be transparent */
.block-container, .main, [data-testid="stHeader"] {
    background: transparent !important;
    background-color: transparent !important;
}
/* Base text styling for Streamlit components to look neon */
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
    text-shadow: 0 0 20px rgba(0, 234, 255, 0.4);
    text-align: center;
    color: #ffffff !important;
}
[data-testid="stMarkdownContainer"] p {
    color: #cbd5e1 !important;
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
}
/* Primary button glow */
[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(0, 198, 255, 0.4) !important;
    transition: all 0.3s ease !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    color: white !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0, 198, 255, 0.6) !important;
}
</style>
</div>""", unsafe_allow_html=True)
        
        st.markdown('<div class="page-section">', unsafe_allow_html=True)
        st.title("🎯 InterviewSense AI")
        st.subheader("Real-Time Interview Performance Analyzer")
        st.write("Simulate a real interview environment. We will ask you questions, analyze your behavioral responses via webcam, and provide detailed feedback.")
        st.write("---")
        
        if st.button("Start Interview", type="primary", use_container_width=True):
            st.session_state.current_page = 'mode_selection'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_tab == "About":
        # CSS specific to the About tab to turn st.columns into distinct glass cards
        st.markdown("""
        <style>
        div[data-testid="stColumns"], div[data-testid="stHorizontalBlock"] {
            background: linear-gradient(145deg, #0b1120, #0f172a) !important;
            border: 1px solid rgba(56, 189, 248, 0.15) !important;
            border-radius: 12px;
            padding: 24px 32px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
            transition: all 0.3s ease;
            align-items: center;
        }

        div[data-testid="stColumns"]:has([class^="marker-"]):hover, div[data-testid="stHorizontalBlock"]:has([class^="marker-"]):hover {
            border: 1px solid rgba(56, 189, 248, 0.6) !important;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.15) !important;
            transform: translateY(-3px) !important;
        }

        .card-heading {
            font-size: 22px;
            font-weight: 600;
            color: #38bdf8;
            margin-bottom: 12px;
            text-align: left;
            font-family: sans-serif;
            letter-spacing: 0.5px;
        }

        /* Remove phantom Streamlit paragraph margins to equalize vertical padding */
        div[data-testid="stColumns"] p, div[data-testid="stHorizontalBlock"] p {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }

        .card-text {
            color: #94a3b8;
            line-height: 1.6;
            font-size: 15px;
            text-align: left;
            margin: 0;
            max-width: 100%;
        }

        .card-icon {
            font-size: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            filter: drop-shadow(0 0 25px rgba(56, 189, 248, 0.5));
            text-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
            margin: 0;
            line-height: 1;
        }
        </style>
        """, unsafe_allow_html=True)

        # ABOUT SECTION
        st.markdown("<h2 class='section-title' style='margin-top: -80px; margin-bottom: 3rem;'>About InterviewSense AI</h2>", unsafe_allow_html=True)
        
        # BOX 1
        col1, col2 = st.columns([3, 1], gap="large")
        with col1:
            st.markdown("<div class='marker-1'></div><div class='card-heading'>Overview</div><div class='card-text'>InterviewSense AI is an intelligent interview simulation platform designed to evaluate communication skills, confidence, and behavioral responses in real-time. By leveraging webcam and speech analysis, it recreates realistic interview scenarios and delivers detailed, actionable feedback to help users improve their performance.</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class='card-icon'>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
              <defs>
                <linearGradient id="robotGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#ffffff"/>
                  <stop offset="100%" stop-color="#38bdf8"/>
                </linearGradient>
                <filter id="robotGlow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <circle cx="10" cy="30" r="1.5" fill="#38bdf8" filter="url(#robotGlow)"/>
              <circle cx="20" cy="80" r="1" fill="#38bdf8" filter="url(#robotGlow)"/>
              <circle cx="85" cy="25" r="1.5" fill="#38bdf8" filter="url(#robotGlow)"/>
              <circle cx="90" cy="70" r="1" fill="#38bdf8" filter="url(#robotGlow)"/>
              <rect x="48" y="15" width="4" height="15" fill="#38bdf8"/>
              <circle cx="50" cy="15" r="5" fill="#a5f3fc" filter="url(#robotGlow)"/>
              <rect x="15" y="45" width="12" height="24" rx="6" fill="#38bdf8"/>
              <rect x="73" y="45" width="12" height="24" rx="6" fill="#38bdf8"/>
              <rect x="22" y="30" width="56" height="44" rx="22" fill="url(#robotGrad)"/>
              <rect x="28" y="38" width="44" height="28" rx="14" fill="#0f172a"/>
              <path d="M 36 48 Q 40 43 44 48" stroke="#a5f3fc" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#robotGlow)"/>
              <path d="M 56 48 Q 60 43 64 48" stroke="#a5f3fc" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#robotGlow)"/>
              <path d="M 43 55 Q 50 60 57 55" stroke="#a5f3fc" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#robotGlow)"/>
            </svg>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # BOX 2
        col1, col2 = st.columns([1, 3], gap="large")
        with col1:
            st.markdown("""<div class='card-icon'>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
              <defs>
                <filter id="eyeGlow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <filter id="strongGlow">
                  <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <linearGradient id="eyeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#0ea5e9"/>
                  <stop offset="100%" stop-color="#1e3a8a"/>
                </linearGradient>
              </defs>
              <circle cx="15" cy="40" r="1" fill="#38bdf8" filter="url(#eyeGlow)"/>
              <circle cx="85" cy="60" r="1.5" fill="#38bdf8" filter="url(#eyeGlow)"/>
              <circle cx="25" cy="85" r="1" fill="#38bdf8" filter="url(#eyeGlow)"/>
              <path d="M 30 20 L 20 20 L 20 30" stroke="#38bdf8" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#eyeGlow)"/>
              <path d="M 70 20 L 80 20 L 80 30" stroke="#38bdf8" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#eyeGlow)"/>
              <path d="M 30 80 L 20 80 L 20 70" stroke="#38bdf8" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#eyeGlow)"/>
              <path d="M 70 80 L 80 80 L 80 70" stroke="#38bdf8" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#eyeGlow)"/>
              <path d="M 15 50 Q 50 15 85 50 Q 50 85 15 50" fill="#1e293b"/>
              <path d="M 15 50 Q 50 15 85 50 Q 50 85 15 50" fill="url(#eyeGrad)"/>
              <circle cx="50" cy="50" r="18" fill="#bae6fd" filter="url(#strongGlow)"/>
              <circle cx="50" cy="50" r="14" fill="#0284c7"/>
              <circle cx="50" cy="50" r="8" fill="#0f172a"/>
              <circle cx="52" cy="48" r="3" fill="#ffffff" filter="url(#eyeGlow)"/>
            </svg>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='marker-2'></div><div class='card-heading'>Behavior Analysis</div><div class='card-text'>The system dynamically analyzes user responses through video and audio inputs, capturing key behavioral cues such as facial expressions, tone, and speaking patterns. Using AI-driven models, it evaluates performance instantly and provides structured feedback to guide improvement step by step.</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # BOX 3
        col1, col2 = st.columns([3, 1], gap="large")
        with col1:
            st.markdown("<div class='marker-3'></div><div class='card-heading'>Key Features</div><div class='card-text'>InterviewSense AI offers a range of powerful features including real-time feedback, confidence analysis, communication scoring, and performance tracking. These features work together to give users a complete understanding of their strengths and areas that need improvement.</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class='card-icon'>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
              <defs>
                <filter id="barGlow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#4ade80"/>
                  <stop offset="100%" stop-color="#166534"/>
                </linearGradient>
                <linearGradient id="blueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#38bdf8"/>
                  <stop offset="100%" stop-color="#1e3a8a"/>
                </linearGradient>
                <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#c084fc"/>
                  <stop offset="100%" stop-color="#6b21a8"/>
                </linearGradient>
              </defs>
              <circle cx="15" cy="50" r="1" fill="#c084fc" filter="url(#barGlow)"/>
              <circle cx="85" cy="30" r="1.5" fill="#38bdf8" filter="url(#barGlow)"/>
              <rect x="20" y="20" width="60" height="60" rx="12" fill="#1e293b" stroke="#334155" stroke-width="2"/>
              <rect x="30" y="45" width="10" height="25" rx="3" fill="url(#greenGrad)" filter="url(#barGlow)"/>
              <rect x="45" y="30" width="10" height="40" rx="3" fill="url(#blueGrad)" filter="url(#barGlow)"/>
              <rect x="60" y="40" width="10" height="30" rx="3" fill="url(#purpleGrad)" filter="url(#barGlow)"/>
            </svg>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # BOX 4
        col1, col2 = st.columns([1, 3], gap="large")
        with col1:
            st.markdown("""<div class='card-icon'>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
              <defs>
                <filter id="rocketGlow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <linearGradient id="rocketBody" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#ffffff"/>
                  <stop offset="100%" stop-color="#94a3b8"/>
                </linearGradient>
                <linearGradient id="flameGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#fef08a"/>
                  <stop offset="100%" stop-color="#f97316"/>
                </linearGradient>
              </defs>
              <circle cx="20" cy="20" r="1.5" fill="#38bdf8" filter="url(#rocketGlow)"/>
              <circle cx="80" cy="80" r="1" fill="#f97316" filter="url(#rocketGlow)"/>
              <g transform="translate(50, 50) rotate(45) translate(-50, -50)">
                <path d="M 40 80 Q 50 100 60 80 Q 50 85 40 80" fill="url(#flameGrad)" filter="url(#rocketGlow)"/>
                <path d="M 35 60 L 25 75 L 35 70 Z" fill="#ef4444"/>
                <path d="M 65 60 L 75 75 L 65 70 Z" fill="#ef4444"/>
                <path d="M 50 10 Q 30 30 35 70 L 65 70 Q 70 30 50 10" fill="url(#rocketBody)"/>
                <circle cx="50" cy="45" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
                <circle cx="50" cy="45" r="5" fill="#38bdf8" filter="url(#rocketGlow)"/>
              </g>
            </svg>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='marker-4'></div><div class='card-heading'>Interview Practice</div><div class='card-text'>Practicing interviews in a simulated environment helps reduce anxiety and builds confidence. By identifying common mistakes and improving communication skills, users can approach real interviews with clarity, preparation, and a stronger presence.</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # BOX 5
        col1, col2 = st.columns([3, 1], gap="large")
        with col1:
            st.markdown("<div class='marker-5'></div><div class='card-heading'>Continuous Growth</div><div class='card-text'>InterviewSense AI is not just a tool, but a learning companion that evolves with you. With continuous feedback and insights, it empowers users to grow consistently, refine their skills, and achieve success in competitive interview environments.</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class='card-icon'>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
              <defs>
                <filter id="plantGlow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <linearGradient id="leafGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#22c55e"/>
                  <stop offset="100%" stop-color="#86efac"/>
                </linearGradient>
                <linearGradient id="potGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#1e293b"/>
                  <stop offset="100%" stop-color="#0f172a"/>
                </linearGradient>
              </defs>
              <circle cx="20" cy="50" r="1" fill="#4ade80" filter="url(#plantGlow)"/>
              <circle cx="80" cy="40" r="1.5" fill="#4ade80" filter="url(#plantGlow)"/>
              <circle cx="30" cy="80" r="1" fill="#38bdf8" filter="url(#plantGlow)"/>
              <path d="M 50 65 Q 20 60 25 35 Q 40 30 50 65" fill="url(#leafGrad)" filter="url(#plantGlow)"/>
              <path d="M 50 65 Q 80 50 75 25 Q 60 20 50 65" fill="url(#leafGrad)" filter="url(#plantGlow)"/>
              <path d="M 50 65 L 50 75" stroke="#22c55e" stroke-width="3" fill="none"/>
              <rect x="35" y="75" width="30" height="10" rx="3" fill="url(#potGrad)"/>
              <rect x="40" y="85" width="20" height="5" rx="2" fill="#38bdf8" filter="url(#plantGlow)"/>
            </svg>
            </div>""", unsafe_allow_html=True)

    elif st.session_state.current_tab == "Features":
        # FEATURES SECTION
        st.markdown("""
            <div class="page-section">
                <div class="section-title">Platform Features</div>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">👁️</div>
                        <div class="feature-title">Core AI Analysis</div>
                        <div class="feature-desc">Real-time behavior analysis, eye contact detection, and confidence tracking.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎙️</div>
                        <div class="feature-title">Speech & Communication</div>
                        <div class="feature-desc">Speech recognition, fluency analysis, and filler word detection.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⏱️</div>
                        <div class="feature-title">Interview Simulation</div>
                        <div class="feature-desc">Automatic question flow, dynamic timers, and real interview environment.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">Smart Feedback</div>
                        <div class="feature-desc">Performance scoring, detailed actionable feedback, and speech validation.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-title">UX Enhancements</div>
                        <div class="feature-desc">Continuous camera tracking, smooth transitions, and progress indicators.</div>
                    </div>
                    <!-- 3 NEW CARDS -->
                    <div class="feature-card">
                        <div class="feature-icon">👀</div>
                        <div class="feature-title">Eye Contact Tracking</div>
                        <div class="feature-desc">Advanced analysis of screen engagement to ensure realistic interactions.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎭</div>
                        <div class="feature-title">Emotion Detection</div>
                        <div class="feature-desc">Tracks facial expressions to determine nervousness and confidence.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📈</div>
                        <div class="feature-title">Performance Analytics</div>
                        <div class="feature-desc">A comprehensive final dashboard highlighting strengths and weaknesses.</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    elif st.session_state.current_tab == "Guidelines":
        # GUIDELINES SECTION
        components.html("""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  html, body { margin: 0; padding: 0; background: transparent; }
  body { display: flex; justify-content: center; }
              .guidelines-section {
                width: min(1400px, 100%);
                margin: 0 auto;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
                padding-top: 2.8rem;
                padding-bottom: 3rem;
              }

              .guidelines-header {
                text-align: center;
                margin-top: -0.25rem;
                margin-bottom: 2.6rem;
              }

              .guidelines-title {
                font-size: 3.1rem;
                font-weight: 800;
                letter-spacing: 0.5px;
                color: #ffffff;
                text-shadow: 0 0 18px rgba(56, 189, 248, 0.18);
                line-height: 1.15;
                margin-bottom: 0.85rem;
              }

              .guidelines-subtitle {
                max-width: 820px;
                margin: 0 auto;
                color: rgba(248, 250, 252, 0.72);
                font-size: 1.08rem;
                line-height: 1.7;
                text-shadow: none;
              }

              .guidelines-grid {
                width: 100%;
                display: grid;
                grid-template-columns: 1fr 1fr;
                column-gap: 0;
                row-gap: 0;
                margin-top: 0.75rem;
              }

              .guideline-block {
                display: flex;
                gap: 1.25rem;
                padding: 1.55rem 1.7rem;
                align-items: flex-start;
                transition: transform 0.25s ease, filter 0.25s ease;
              }

              /* Subtle quadrant separators like the reference (not cards) */
              .g-border-right { border-right: 1px solid rgba(148, 163, 184, 0.18); }
              .g-border-bottom { border-bottom: 1px solid rgba(148, 163, 184, 0.18); }

              .guideline-block:hover {
                transform: translateX(4px);
              }

              .g-icon-wrap {
                width: 70px;
                height: 70px;
                border-radius: 999px;
                border: 1px solid rgba(56, 189, 248, 0.50);
                background: rgba(2, 6, 23, 0.25);
                box-shadow:
                  0 0 26px rgba(56, 189, 248, 0.24),
                  inset 0 0 16px rgba(56, 189, 248, 0.11);
                display: flex;
                align-items: center;
                justify-content: center;
                flex: 0 0 70px;
                transition: box-shadow 0.25s ease, border-color 0.25s ease, filter 0.25s ease;
              }

              .guideline-block:hover .g-icon-wrap {
                border-color: rgba(56, 189, 248, 0.75);
                box-shadow:
                  0 0 30px rgba(56, 189, 248, 0.32),
                  inset 0 0 18px rgba(56, 189, 248, 0.14);
              }

              .g-icon {
                width: 32px;
                height: 32px;
              }

              .g-icon path, .g-icon circle, .g-icon line, .g-icon polyline, .g-icon rect {
                stroke: #38bdf8;
                stroke-width: 2;
                fill: none;
                stroke-linecap: round;
                stroke-linejoin: round;
              }

              .g-content { flex: 1; }

              .g-head {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-top: 0.1rem;
                margin-bottom: 0.6rem;
              }

              .g-title {
                font-size: 1.12rem;
                font-weight: 700;
                color: rgba(56, 189, 248, 0.95);
                margin: 0;
              }

              .g-points {
                margin: 0;
                padding-left: 1.1rem;
              }

              .g-points li {
                margin: 0.4rem 0;
                color: rgba(248, 250, 252, 0.84);
                font-size: 0.98rem;
                line-height: 1.55;
                white-space: normal;
              }

              .g-points li::marker {
                color: rgba(56, 189, 248, 0.95);
              }

              /* Keep 2-column layout for typical Streamlit widths (~850px) */
              @media (max-width: 700px) {
                .guidelines-title { font-size: 2.4rem; }
                .guidelines-grid { grid-template-columns: 1fr; }
                .g-border-right { border-right: none; }
                .guideline-block { border-bottom: 1px solid rgba(148, 163, 184, 0.18); }
                .g-points li { white-space: normal; }
              }
</style>
</head>
<body>

<div class="page-section guidelines-section">
  <div class="guidelines-header">
    <div class="guidelines-title">Interview Guidelines</div>
    <div class="guidelines-subtitle">
      Follow these best practices to perform your best and make a great impression in your interview.
    </div>
  </div>

  <div class="guidelines-grid">
                <!-- Row 1 -->
                <div class="guideline-block g-border-right g-border-bottom">
                  <div class="g-icon-wrap">
                    <!-- chat bubble -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M20 13a6 6 0 0 1-6 6H8l-4 3V7a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6z"></path>
                      <line x1="8" y1="8" x2="16" y2="8"></line>
                      <line x1="8" y1="12" x2="14" y2="12"></line>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">1. Communication</div></div>
                    <ul class="g-points">
                      <li>Speak clearly and confidently</li>
                      <li>Avoid filler words like "um", "uh", "like"</li>
                      <li>Speak naturally and at a moderate pace</li>
                    </ul>
                  </div>
                </div>

                <div class="guideline-block g-border-bottom">
                  <div class="g-icon-wrap">
                    <!-- eye -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"></path>
                      <circle cx="12" cy="12" r="3.2"></circle>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">2. Eye Contact &amp; Focus</div></div>
                    <ul class="g-points">
                      <li>Maintain eye contact with the camera</li>
                      <li>Stay focused and avoid looking away frequently</li>
                      <li>Show attentiveness throughout</li>
                    </ul>
                  </div>
                </div>

                <!-- Row 2 -->
                <div class="guideline-block g-border-right g-border-bottom">
                  <div class="g-icon-wrap">
                    <!-- posture (seated person) -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <circle cx="9" cy="6.3" r="2.1"></circle>
                      <path d="M8.2 8.8l3.3 2.4h3.6"></path>
                      <path d="M10.1 11.1l-1.1 3.7"></path>
                      <path d="M12.2 11.6l1.2 3.8"></path>
                      <!-- chair -->
                      <path d="M15.8 10.3v5.2"></path>
                      <path d="M15.8 15.5h3.4"></path>
                      <path d="M6.0 20h13.0"></path>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">3. Posture &amp; Body Language</div></div>
                    <ul class="g-points">
                      <li>Sit upright with a professional posture</li>
                      <li>Avoid unnecessary movements or fidgeting</li>
                      <li>Keep gestures natural and controlled</li>
                    </ul>
                  </div>
                </div>

                <div class="guideline-block g-border-bottom">
                  <div class="g-icon-wrap">
                    <!-- light bulb -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M9 18h6"></path>
                      <path d="M10 22h4"></path>
                      <path d="M8 10a4 4 0 1 1 8 0c0 2-1.2 3-2.2 4.2-.4.5-.8 1.1-.8 1.8H11c0-.7-.4-1.3-.8-1.8C9.2 13 8 12 8 10z"></path>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">4. Environment</div></div>
                    <ul class="g-points">
                      <li>Ensure proper lighting on your face</li>
                      <li>Avoid background noise and distractions</li>
                      <li>Keep your setup clean and professional</li>
                    </ul>
                  </div>
                </div>

                <!-- Row 3 -->
                <div class="guideline-block g-border-right">
                  <div class="g-icon-wrap">
                    <!-- document/pencil -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M7 3h7l3 3v15a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"></path>
                      <path d="M14 3v4h4"></path>
                      <path d="M9 14l7-7 2 2-7 7H9z"></path>
                      <path d="M9 14v3h3"></path>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">5. Answering Approach</div></div>
                    <ul class="g-points">
                      <li>Understand the question before answering</li>
                      <li>Structure answers clearly and logically</li>
                      <li>Keep responses relevant and concise</li>
                    </ul>
                  </div>
                </div>

                <div class="guideline-block">
                  <div class="g-icon-wrap">
                    <!-- target -->
                    <svg class="g-icon" viewBox="0 0 24 24" aria-hidden="true">
                      <circle cx="12" cy="12" r="8"></circle>
                      <circle cx="12" cy="12" r="4"></circle>
                      <path d="M12 2v3"></path>
                      <path d="M22 12h-3"></path>
                      <path d="M12 22v-3"></path>
                      <path d="M2 12h3"></path>
                    </svg>
                  </div>
                  <div class="g-content">
                    <div class="g-head"><div class="g-title">6. Preparation &amp; Professionalism</div></div>
                    <ul class="g-points">
                      <li>Be ready before the interview starts</li>
                      <li>Maintain calm and confidence</li>
                      <li>Treat it like a real interview situation</li>
                    </ul>
                  </div>
                </div>
  </div>
</div>
</body>
</html>
        """, height=1220, scrolling=False)

def start_mock_interview():
    """Initializes and starts the original HR/Behavioural mock interview."""
    st.session_state.current_page = 'interview'
    
    # Select 5 questions
    selected_pool = random.sample(QUESTION_POOL, 4)
    st.session_state.current_questions = ["Tell me about yourself"] + selected_pool
    
    st.session_state.question_index = 0
    st.session_state.video_results = []
    st.session_state.audio_results = []
    st.session_state.question_spoken = False
    st.session_state.is_recording = False
    st.session_state.analysis_done = False
    st.session_state.hardware_verified = False
    st.session_state.frames = []
    st.rerun()

def render_mode_selection_page():
    """Renders the Interview Mode Selection page with Mock and Technical interview options."""
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Home", key="back_to_home_mode", type="secondary"):
            st.session_state.current_page = 'landing'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.5rem;">', unsafe_allow_html=True)
    st.title("🎯 Choose Your Interview Mode")
    st.subheader("Select the type of interview you want to practice and improve your skills.")
    st.write("---")

    # Scoped styling for mode cards
    st.markdown("""
    <style>
    .mode-card-container {
        background: linear-gradient(145deg, #0b1120, #0f172a);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 28px 24px 20px 24px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    .mode-card-container:hover {
        border-color: #38bdf8;
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(56, 189, 248, 0.2);
    }
    .mode-pill {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 12px;
    }
    .mode-pill-blue {
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .mode-pill-purple {
        background: rgba(168, 85, 247, 0.12);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .mode-card-title {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: left;
    }
    .mode-card-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
        text-align: left;
        margin-bottom: 16px;
    }
    .mode-card-list {
        list-style: none;
        padding: 0;
        margin: 0;
        text-align: left;
    }
    .mode-card-list li {
        color: #cbd5e1;
        font-size: 0.92rem;
        padding: 5px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .mode-card-list li::before {
        content: "✦";
        color: #38bdf8;
        font-weight: bold;
    }
    .mode-card-list.purple li::before {
        color: #c084fc;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card-container">
            <span class="mode-pill mode-pill-blue">HR & Behavioural</span>
            <div class="mode-card-title">Mock Interview</div>
            <div class="mode-card-desc">
                Practice real-world HR and behavioural interview questions to improve your confidence, communication, and interview readiness.
            </div>
            <ul class="mode-card-list">
                <li>HR interview questions</li>
                <li>Behavioural questions</li>
                <li>General interview questions</li>
                <li>Confidence and communication practice</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Mock Interview", key="btn_start_mock", type="primary", use_container_width=True):
            start_mock_interview()

    with col2:
        st.markdown("""
        <div class="mode-card-container">
            <span class="mode-pill mode-pill-purple">Domain & Skills</span>
            <div class="mode-card-title">Technical Interview</div>
            <div class="mode-card-desc">
                Test your technical knowledge with questions based on your selected domain and skills.
            </div>
            <ul class="mode-card-list purple">
                <li>Domain-based questions</li>
                <li>Skill-based questions</li>
                <li>Technical interview practice</li>
                <li>Programming and computer science concepts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Technical Interview", key="btn_start_tech", type="primary", use_container_width=True):
            st.session_state.current_page = 'technical_setup'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

TECHNICAL_DOMAIN_SKILLS = {
    "Python Programming": [
        "Python Basics",
        "OOP in Python",
        "Functions and Modules",
        "Exception Handling",
        "File Handling",
        "Lists, Tuples, Sets and Dictionaries",
        "Libraries and Packages"
    ],
    "Java Programming": [
        "Core Java",
        "OOP Concepts",
        "Collections Framework",
        "Exception Handling",
        "Multithreading",
        "JDBC",
        "Java 8 Features"
    ],
    "C Programming": [
        "C Basics",
        "Pointers",
        "Arrays and Strings",
        "Structures and Unions",
        "Functions",
        "Memory Management",
        "File Handling"
    ],
    "C++ Programming": [
        "C++ Basics",
        "OOP Concepts",
        "Pointers and References",
        "STL",
        "Templates",
        "Memory Management",
        "Exception Handling"
    ],
    "Data Structures and Algorithms": [
        "Arrays",
        "Linked Lists",
        "Stacks and Queues",
        "Trees and Graphs",
        "Searching and Sorting",
        "Hashing",
        "Dynamic Programming",
        "Time and Space Complexity"
    ],
    "Web Development": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "REST APIs",
        "Frontend Development",
        "Backend Development"
    ],
    "Database Management Systems (DBMS)": [
        "DBMS Fundamentals",
        "Relational Database Concepts",
        "Normalization",
        "Transactions",
        "Indexing",
        "Joins",
        "ACID Properties"
    ],
    "SQL": [
        "SQL Basics",
        "SELECT Queries",
        "Joins",
        "Subqueries",
        "Aggregate Functions",
        "Group By and Having",
        "Constraints",
        "Views"
    ],
    "Operating Systems": [
        "Process Management",
        "Threads",
        "CPU Scheduling",
        "Deadlocks",
        "Memory Management",
        "Virtual Memory",
        "File Systems"
    ],
    "Computer Networks": [
        "OSI Model",
        "TCP/IP",
        "IP Addressing",
        "DNS",
        "HTTP and HTTPS",
        "Routing",
        "Network Security Basics"
    ],
    "Artificial Intelligence and Machine Learning": [
        "AI Fundamentals",
        "Machine Learning Basics",
        "Supervised Learning",
        "Unsupervised Learning",
        "Neural Networks",
        "Deep Learning",
        "Natural Language Processing"
    ],
    "Software Engineering": [
        "SDLC",
        "Agile Methodology",
        "Software Testing",
        "Software Design",
        "Design Patterns",
        "Version Control Concepts",
        "Software Maintenance"
    ]
}

def render_technical_setup_page():
    """Renders the Step 2 Technical Interview Domain and Skill Setup Page."""
    # Navigation buttons
    col_nav1, col_nav2, _ = st.columns([1.3, 1, 3])
    with col_nav1:
        if st.button("← Back to Modes", key="back_to_modes_btn", type="secondary"):
            st.session_state.current_page = 'mode_selection'
            st.rerun()
            return
    with col_nav2:
        if st.button("⌂ Back to Home", key="back_to_home_from_setup", type="secondary"):
            st.session_state.current_page = 'landing'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.5rem;">', unsafe_allow_html=True)
    st.title("⚙️ Configure Your Technical Interview")
    st.subheader("Choose your technical domain and skills to generate an interview tailored to your knowledge.")
    st.write("---")

    # Custom styling for setup cards and skill chips
    st.markdown("""
    <style>
    .setup-card {
        background: linear-gradient(145deg, #0b1120, #0f172a);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);
    }
    .setup-step-header {
        color: #38bdf8;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .skill-chip {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #e0f2fe;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    .selected-summary-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px dashed rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    # SECTION 1: DOMAIN SELECTION
    st.markdown('<div class="setup-card">', unsafe_allow_html=True)
    st.markdown('<div class="setup-step-header">📌 1. Select Your Technical Domain</div>', unsafe_allow_html=True)
    st.caption("Select the primary programming language or computer science domain for your interview.")

    domain_list = list(TECHNICAL_DOMAIN_SKILLS.keys())
    current_domain_idx = domain_list.index(st.session_state.technical_domain) if st.session_state.technical_domain in domain_list else 0

    selected_domain = st.selectbox(
        "Technical Domain",
        options=domain_list,
        index=current_domain_idx,
        key="tech_domain_select",
        label_visibility="collapsed"
    )

    # Detect domain change and reset skills
    if selected_domain != st.session_state.previous_technical_domain:
        st.session_state.technical_domain = selected_domain
        st.session_state.previous_technical_domain = selected_domain
        st.session_state.technical_skills = []
        for k in list(st.session_state.keys()):
            if k.startswith("skill_chk_"):
                del st.session_state[k]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 2: SKILL SELECTION
    available_skills = TECHNICAL_DOMAIN_SKILLS[st.session_state.technical_domain]

    st.markdown('<div class="setup-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="setup-step-header">🎯 2. Select Your Skills ({st.session_state.technical_domain})</div>', unsafe_allow_html=True)
    st.caption("Select one or more topics. When you switch domains, skill selections automatically reset.")

    # Select All / Clear Selection Controls
    col_s1, col_s2, _ = st.columns([1, 1.2, 2.5])
    with col_s1:
        if st.button("✓ Select All", key="btn_select_all_skills", type="secondary"):
            st.session_state.technical_skills = list(available_skills)
            for s in available_skills:
                st.session_state[f"skill_chk_{st.session_state.technical_domain}_{s}"] = True
            st.rerun()
    with col_s2:
        if st.button("✕ Clear Selection", key="btn_clear_skills", type="secondary"):
            st.session_state.technical_skills = []
            for s in available_skills:
                st.session_state[f"skill_chk_{st.session_state.technical_domain}_{s}"] = False
            st.rerun()

    # Dynamic Checkboxes in 2 Columns
    col_left, col_right = st.columns(2)
    selected_now = []

    for idx, skill in enumerate(available_skills):
        target_col = col_left if (idx % 2 == 0) else col_right
        chk_key = f"skill_chk_{st.session_state.technical_domain}_{skill}"
        
        # Checkbox state matches technical_skills session state
        checked = target_col.checkbox(
            skill,
            value=(skill in st.session_state.technical_skills),
            key=chk_key
        )
        if checked:
            selected_now.append(skill)

    # Keep session state updated with user's interactive selections
    st.session_state.technical_skills = selected_now

    # Clear display of selected skills
    if st.session_state.technical_skills:
        chips_markup = "".join([f'<span class="skill-chip">{s}</span>' for s in st.session_state.technical_skills])
        st.markdown(f"""
        <div class="selected-summary-box">
            <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 700; margin-bottom: 6px;">
                ACTIVE TOPICS ({len(st.session_state.technical_skills)} SELECTED):
            </div>
            <div>{chips_markup}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please select at least one skill to enable generating the technical interview.")

    st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 3 & 4: DIFFICULTY AND QUESTION COUNT
    col_d, col_q = st.columns(2, gap="large")

    with col_d:
        st.markdown('<div class="setup-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="setup-step-header">📊 3. Interview Difficulty</div>', unsafe_allow_html=True)
        st.caption("Select the question challenge level.")
        
        difficulty_options = ["Beginner", "Intermediate", "Advanced"]
        diff_idx = difficulty_options.index(st.session_state.technical_difficulty) if st.session_state.technical_difficulty in difficulty_options else 1
        
        selected_diff = st.selectbox(
            "Difficulty Level",
            options=difficulty_options,
            index=diff_idx,
            key="tech_diff_select",
            label_visibility="collapsed"
        )
        st.session_state.technical_difficulty = selected_diff
        st.markdown('</div>', unsafe_allow_html=True)

    with col_q:
        st.markdown('<div class="setup-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="setup-step-header">🔢 4. Number of Questions</div>', unsafe_allow_html=True)
        st.caption("Select the total question length.")
        
        question_count_options = ["5 Questions", "10 Questions", "15 Questions"]
        count_idx = question_count_options.index(st.session_state.technical_num_questions) if st.session_state.technical_num_questions in question_count_options else 0
        
        selected_count = st.selectbox(
            "Questions Count",
            options=question_count_options,
            index=count_idx,
            key="tech_num_q_select",
            label_visibility="collapsed"
        )
        st.session_state.technical_num_questions = selected_count
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # SECTION 5: GENERATE TECHNICAL INTERVIEW BUTTON WITH VALIDATION & GENERATION ENGINE
    if st.button("🚀 Generate Technical Interview", key="btn_generate_tech_interview", type="primary", use_container_width=True):
        # Validations
        if not st.session_state.technical_domain:
            st.error("Please select a technical domain.")
        elif not st.session_state.technical_skills:
            st.error("⚠️ Please select at least one skill before proceeding to generate the technical interview.")
        elif not st.session_state.technical_difficulty:
            st.error("Please select an interview difficulty.")
        else:
            # Parse requested question count
            try:
                num_q = int(str(st.session_state.technical_num_questions).split()[0])
            except Exception:
                num_q = 5
                
            # Generate technical questions from the question bank
            generated_qs = generate_technical_questions(
                domain=st.session_state.technical_domain,
                skills=st.session_state.technical_skills,
                difficulty=st.session_state.technical_difficulty,
                num_questions=num_q
            )
            
            if not generated_qs:
                st.error("Unable to find questions matching the selected criteria. Please select additional skills.")
            else:
                st.session_state.technical_questions = generated_qs
                st.session_state.technical_question_index = 0
                st.session_state.technical_answers = {}
                st.session_state.technical_interview_completed = False
                st.session_state.technical_interview_submitted = False
                st.session_state.confirm_end_technical = False
                st.session_state.confirm_submit_technical = False
                st.session_state.technical_evaluation_results = None
                st.session_state.technical_overall_score = 0
                st.session_state.technical_performance_level = "Needs Improvement"
                st.session_state.technical_evaluation_completed = False
                # Clear previous technical answer input session keys
                for k in list(st.session_state.keys()):
                    if k.startswith("tech_ans_input_") or k.startswith("voice_dur_"):
                        del st.session_state[k]
                st.session_state.current_page = 'technical_interview'
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_technical_interview_page():
    """Renders the interactive Step 4 Technical Interview Question and Answer Interface."""
    if not st.session_state.technical_questions:
        st.session_state.current_page = 'technical_setup'
        st.rerun()
        return

    total_q = len(st.session_state.technical_questions)
    curr_idx = st.session_state.technical_question_index
    curr_q_num = curr_idx + 1
    curr_q_data = st.session_state.technical_questions[curr_idx]

    # Calculate answered and unanswered stats
    answered_count = sum(
        1 for i in range(total_q)
        if st.session_state.technical_answers.get(i, {}).get("answer_text", "").strip() != ""
    )
    unanswered_count = total_q - answered_count

    # Top Sub-Navigation and Live Counters
    col_t1, col_t2 = st.columns([1.2, 3.8])
    with col_t1:
        if st.button("← Setup Page", key="back_to_setup_from_interview", type="secondary"):
            save_current_technical_answer(curr_idx)
            st.session_state.current_page = 'technical_setup'
            st.rerun()
            return
    with col_t2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 6px;">
            <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.35); padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; margin-right: 8px;">
                ✅ Answered: {answered_count}/{total_q}
            </span>
            <span style="background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.35); padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">
                ⏳ Unanswered: {unanswered_count}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
    
    # Simulation Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge" style="background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.4); color: #7dd3fc;">⚡ Technical Interview Simulation</div></div>', unsafe_allow_html=True)
    
    st.title("💻 Technical Interview")
    
    # Progress Display
    st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 0.5rem;'>Question <strong>{curr_q_num}</strong> of <strong>{total_q}</strong></div>", unsafe_allow_html=True)
    st.progress(curr_q_num / total_q)

    # Scoped styling for question card and answer controls
    st.markdown("""
    <style>
    .tech-question-card {
        background: linear-gradient(145deg, #0b1120, #0f172a);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 28px 24px;
        margin: 1.2rem auto 1.5rem auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
        text-align: left;
    }
    .meta-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 8px;
        margin-bottom: 12px;
    }
    .meta-tag-domain { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .meta-tag-skill { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .meta-tag-diff { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .meta-tag-type { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .tech-q-text {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1.5;
        margin-top: 10px;
        margin-bottom: 8px;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
    }
    .answer-header-box {
        background: rgba(15, 23, 42, 0.7);
        border-left: 4px solid #38bdf8;
        padding: 10px 16px;
        border-radius: 4px;
        margin-bottom: 14px;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render Question Card with Metadata Badges
    q_domain = curr_q_data.get("domain", st.session_state.technical_domain)
    q_skill = curr_q_data.get("skill", "General")
    q_diff = curr_q_data.get("difficulty", st.session_state.technical_difficulty)
    q_type = curr_q_data.get("question_type", "Conceptual")
    q_text = curr_q_data.get("question", "")

    st.markdown(f"""
    <div class="tech-question-card">
        <div>
            <span class="meta-tag meta-tag-domain">{q_domain}</span>
            <span class="meta-tag meta-tag-skill">{q_skill}</span>
            <span class="meta-tag meta-tag-diff">{q_diff}</span>
            <span class="meta-tag meta-tag-type">{q_type}</span>
        </div>
        <div class="tech-q-text">
            Q{curr_q_num}: {q_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Answer Input Section
    st.markdown("""
    <div class="answer-header-box">
        <span style="color: #38bdf8; font-weight: 700; font-size: 1.1rem;">✍️ Your Technical Answer</span>
        <span style="color: #94a3b8; font-size: 0.9rem; margin-left: 10px;">Type your response or use voice recording to dictate. Answers can be edited anytime before submitting.</span>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session input state for this question if absent
    input_key = f"tech_ans_input_{curr_idx}"
    if input_key not in st.session_state:
        existing_val = st.session_state.technical_answers.get(curr_idx, {}).get("answer_text", "")
        st.session_state[input_key] = existing_val

    # Voice Dictation Controls Row
    v_col1, v_col2 = st.columns([1, 2.5])
    with v_col1:
        voice_duration = st.selectbox(
            "Voice Duration",
            [10, 15, 20, 30],
            index=1,
            format_func=lambda s: f"{s} seconds",
            key=f"voice_dur_{curr_idx}",
            label_visibility="collapsed"
        )
    with v_col2:
        if st.button("🎙️ Answer Using Voice", key=f"btn_voice_rec_{curr_idx}", type="secondary", use_container_width=True):
            with st.spinner(f"🎙️ Listening for {voice_duration} seconds... Speak your answer clearly into the microphone."):
                success, transcribed_result = record_technical_voice_answer(duration=voice_duration)
                if success:
                    prev_text = st.session_state.get(input_key, "").strip()
                    if prev_text:
                        combined_text = f"{prev_text} {transcribed_result}"
                    else:
                        combined_text = transcribed_result
                    st.session_state[input_key] = combined_text
                    save_current_technical_answer(curr_idx, method="voice")
                    st.success(f"✅ Transcribed: '{transcribed_result}' — Added to your answer below. Feel free to review or edit.")
                    st.rerun()
                else:
                    st.error(f"🎙️ Voice Input Note: {transcribed_result}")

    # Text Area Answer Input
    user_answer = st.text_area(
        "Candidate Response:",
        value=st.session_state[input_key],
        height=190,
        placeholder="Type your answer here...",
        key=input_key,
        label_visibility="collapsed"
    )

    # Dynamic status bar below text area
    curr_answer_clean = user_answer.strip()
    c_info, c_save = st.columns([3, 1])
    with c_info:
        if curr_answer_clean:
            word_count = len(curr_answer_clean.split())
            method = st.session_state.technical_answers.get(curr_idx, {}).get("answer_method", "text")
            st.markdown(f"<div style='padding-top: 8px; color: #4ade80; font-size: 0.92rem;'>✅ Answer recorded for Question {curr_q_num} ({word_count} words • Method: {method.capitalize()})</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding-top: 8px; color: #94a3b8; font-size: 0.92rem;'>⚪ No answer saved yet for Question {curr_q_num}. (You can still proceed to other questions)</div>", unsafe_allow_html=True)
    with c_save:
        if st.button("💾 Save Answer", key=f"btn_save_{curr_idx}", type="secondary", use_container_width=True):
            save_current_technical_answer(curr_idx)
            st.success("Answer saved!")
            st.rerun()

    # Submission Confirmation Prompt
    if st.session_state.confirm_submit_technical:
        st.markdown('<div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; border-radius: 12px; padding: 22px; margin: 24px 0; box-shadow: 0 4px 25px rgba(56, 189, 248, 0.25);">', unsafe_allow_html=True)
        if unanswered_count > 0:
            st.warning(f"⚠️ You have **{unanswered_count} unanswered question(s)** out of **{total_q}**. Are you sure you want to submit your technical interview now?")
        else:
            st.success("🎉 All questions have recorded answers! Ready to submit your technical interview?")
        
        col_s_yes, col_s_no = st.columns(2)
        with col_s_yes:
            if st.button("✓ Yes, Submit Interview Now", key="confirm_submit_yes_btn", type="primary", use_container_width=True):
                save_current_technical_answer(curr_idx)
                st.session_state.confirm_submit_technical = False
                st.session_state.technical_interview_submitted = True
                st.session_state.technical_interview_completed = True
                st.session_state.current_page = 'technical_submission'
                st.rerun()
        with col_s_no:
            if st.button("Cancel & Continue Reviewing", key="confirm_submit_no_btn", type="secondary", use_container_width=True):
                st.session_state.confirm_submit_technical = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Confirmation box if user clicked End Interview Early
    if st.session_state.confirm_end_technical:
        st.markdown('<div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; margin: 20px 0;">', unsafe_allow_html=True)
        st.warning("⚠️ Are you sure you want to exit without finishing? Your recorded answers will be submitted as-is.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, End & View Summary", key="confirm_end_yes", type="primary", use_container_width=True):
                save_current_technical_answer(curr_idx)
                st.session_state.confirm_end_technical = False
                st.session_state.technical_interview_completed = True
                st.session_state.technical_interview_submitted = True
                st.session_state.current_page = 'technical_submission'
                st.rerun()
        with col_no:
            if st.button("Cancel", key="confirm_end_no", type="secondary", use_container_width=True):
                st.session_state.confirm_end_technical = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # Bottom Navigation Controls
    col_prev, col_middle, col_next = st.columns([1.2, 1, 1.2])

    with col_prev:
        if st.button("← Previous Question", key="btn_prev_tech_q", disabled=(curr_idx == 0), type="secondary", use_container_width=True):
            save_current_technical_answer(curr_idx)
            st.session_state.technical_question_index -= 1
            st.session_state.confirm_end_technical = False
            st.session_state.confirm_submit_technical = False
            st.rerun()

    with col_middle:
        if not st.session_state.confirm_end_technical and not st.session_state.confirm_submit_technical:
            if st.button("⏹ End Interview", key="btn_end_tech_q", type="secondary", use_container_width=True):
                st.session_state.confirm_end_technical = True
                st.session_state.confirm_submit_technical = False
                st.rerun()

    with col_next:
        if curr_idx < total_q - 1:
            if st.button("Next Question →", key="btn_next_tech_q", type="primary", use_container_width=True):
                save_current_technical_answer(curr_idx)
                st.session_state.technical_question_index += 1
                st.session_state.confirm_end_technical = False
                st.session_state.confirm_submit_technical = False
                st.rerun()
        else:
            if st.button("Submit Interview 🚀", key="btn_finish_tech_q", type="primary", use_container_width=True):
                save_current_technical_answer(curr_idx)
                st.session_state.confirm_submit_technical = True
                st.session_state.confirm_end_technical = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_technical_submission_page():
    """Renders the Step 4 Technical Interview Submission Summary and Candidate Answer Review Page."""
    st.markdown('<div class="page-section" style="padding-top: 1rem;">', unsafe_allow_html=True)
    
    st.title("🎉 Technical Interview Submitted!")
    st.subheader("Your responses have been successfully submitted. Your technical performance analysis is the next step.")
    st.write("---")

    total_q = len(st.session_state.technical_questions)
    answered_count = sum(
        1 for i in range(total_q)
        if st.session_state.technical_answers.get(i, {}).get("answer_text", "").strip() != ""
    )
    unanswered_count = total_q - answered_count
    completion_rate = int((answered_count / total_q) * 100) if total_q > 0 else 0

    # Skills badge list
    skills_badges = "".join([f'<span class="skill-chip">{s}</span>' for s in st.session_state.technical_skills])

    # Session Summary Card
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 16px; padding: 28px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45); max-width: 820px; margin: 1.5rem auto; text-align: left;">
        <div style="text-align: center; font-size: 3.2rem; margin-bottom: 8px;">📋</div>
        <h2 style="color: #38bdf8; text-align: center; margin-bottom: 6px;">Submission Summary</h2>
        <p style="text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 20px;">
            Domain: <strong style="color: #ffffff;">{st.session_state.technical_domain}</strong> • Difficulty: <strong style="color: #ffffff;">{st.session_state.technical_difficulty}</strong>
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; text-align: center;">
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Total Questions</div>
                <div style="color: #38bdf8; font-size: 1.6rem; font-weight: 800;">{total_q}</div>
            </div>
            <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 10px; padding: 12px;">
                <div style="color: #4ade80; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Answered</div>
                <div style="color: #4ade80; font-size: 1.6rem; font-weight: 800;">{answered_count}</div>
            </div>
            <div style="background: rgba(251, 146, 60, 0.1); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 10px; padding: 12px;">
                <div style="color: #fb923c; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Unanswered</div>
                <div style="color: #fb923c; font-size: 1.6rem; font-weight: 800;">{unanswered_count}</div>
            </div>
            <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 10px; padding: 12px;">
                <div style="color: #c084fc; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Completion</div>
                <div style="color: #c084fc; font-size: 1.6rem; font-weight: 800;">{completion_rate}%</div>
            </div>
        </div>

        <div>
            <div style="color: #38bdf8; font-weight: 700; margin-bottom: 8px; font-size: 0.9rem;">TOPICS PRACTICED:</div>
            <div>{skills_badges}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detailed Question and Answer Breakdown Accordion
    st.subheader("🔍 Review Submitted Answers")
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem;'>Review each question and your corresponding text or voice responses before moving to analysis.</p>", unsafe_allow_html=True)

    for i, q_data in enumerate(st.session_state.technical_questions):
        ans_entry = st.session_state.technical_answers.get(i, {})
        ans_text = ans_entry.get("answer_text", "").strip()
        ans_method = ans_entry.get("answer_method", "text")
        is_answered = bool(ans_text)
        status_label = "✅ Answered" if is_answered else "⚠️ Unanswered"
        
        q_title = f"{status_label} — Q{i+1}: {q_data.get('question')}"
        with st.expander(q_title, expanded=(i == 0)):
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span class="meta-tag meta-tag-skill">{q_data.get('skill', 'General')}</span>
                <span class="meta-tag meta-tag-diff">{q_data.get('difficulty', st.session_state.technical_difficulty)}</span>
                <span class="meta-tag meta-tag-type">{q_data.get('question_type', 'Conceptual')}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Question:** {q_data.get('question')}")
            st.write("---")
            if is_answered:
                st.markdown(f"**Your Submitted Response:** *(Recorded via {ans_method.capitalize()} • {len(ans_text.split())} words)*")
                st.info(ans_text)
            else:
                st.warning("⚠️ No answer was provided for this question.")

    st.write("---")

    # Primary Action: Continue to Analysis (Step 5)
    col_a1, col_a2, col_a3 = st.columns([1.5, 1.2, 1])
    with col_a1:
        if st.button("Continue to Analysis →", key="btn_goto_analysis", type="primary", use_container_width=True):
            st.session_state.current_page = 'technical_analysis'
            st.rerun()
    with col_a2:
        if st.button("Practice Another Topic", key="btn_new_tech_setup_sub", type="secondary", use_container_width=True):
            st.session_state.current_page = 'technical_setup'
            st.rerun()
    with col_a3:
        if st.button("Mode Selection", key="btn_return_mode_sub", type="secondary", use_container_width=True):
            st.session_state.current_page = 'mode_selection'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_technical_analysis_page():
    """Renders the Step 5 Technical Answer Evaluation and Performance Analysis Page."""
    if not st.session_state.get("technical_questions"):
        st.session_state.current_page = 'technical_setup'
        st.rerun()
        return

    # Trigger evaluation if not yet completed for this session
    if not st.session_state.get("technical_evaluation_completed") or st.session_state.get("technical_evaluation_results") is None:
        with st.spinner("🧠 Evaluating your technical responses across accuracy, depth, relevance, and completeness..."):
            time.sleep(0.8) # UX transition indicator
            results = evaluate_technical_interview(
                st.session_state.technical_questions,
                st.session_state.technical_answers
            )
            st.session_state.technical_evaluation_results = results
            st.session_state.technical_overall_score = results["overall_score"]
            st.session_state.technical_performance_level = results["performance_level"]
            st.session_state.technical_evaluation_completed = True
            st.rerun()
            return

    results = st.session_state.technical_evaluation_results
    overall_sc = results.get("overall_score", 0)
    perf_level = results.get("performance_level", "Good")

    # Styling for performance classification badge and theme
    if perf_level == "Excellent":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#4ade80", "rgba(34, 197, 94, 0.15)", "rgba(34, 197, 94, 0.4)", "🌟"
    elif perf_level == "Very Good":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#38bdf8", "rgba(56, 189, 248, 0.15)", "rgba(56, 189, 248, 0.4)", "✅"
    elif perf_level == "Good":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#facc15", "rgba(250, 204, 21, 0.15)", "rgba(250, 204, 21, 0.4)", "👍"
    elif perf_level == "Needs Improvement":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#fb923c", "rgba(251, 146, 60, 0.15)", "rgba(251, 146, 60, 0.4)", "⚠️"
    else:
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#f87171", "rgba(239, 68, 68, 0.15)", "rgba(239, 68, 68, 0.4)", "❌"

    # Top Sub-Navigation
    col_t1, col_t2 = st.columns([1.5, 3.5])
    with col_t1:
        if st.button("← Submission Summary", key="btn_back_to_sub_top", type="secondary"):
            st.session_state.current_page = 'technical_submission'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
    
    # Evaluation Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge" style="background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.4); color: #7dd3fc;">⚡ Technical Evaluation Engine (Step 5)</div></div>', unsafe_allow_html=True)
    
    st.title("📊 Technical Answer Analysis")
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 1.5rem;'>Detailed evaluation of your answers based on technical correctness, conceptual depth, relevance, and explanation quality.</p>", unsafe_allow_html=True)

    # 1. Performance Overview Dashboard Card
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 18px; padding: 32px 28px; box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5); max-width: 860px; margin: 1rem auto 2rem auto; text-align: center;">
        <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">OVERALL TECHNICAL INTERVIEW SCORE</div>
        <div style="font-size: 3.8rem; font-weight: 900; color: #38bdf8; line-height: 1; margin-bottom: 12px; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);">
            {overall_sc}<span style="font-size: 1.8rem; color: #64748b; font-weight: 600;">/100</span>
        </div>
        <div style="margin-bottom: 24px;">
            <span style="display: inline-block; padding: 6px 20px; border-radius: 20px; font-weight: 700; font-size: 1.1rem; color: {lvl_color}; background: {lvl_bg}; border: 1px solid {lvl_border};">
                {lvl_icon} Classification: {perf_level}
            </span>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; text-align: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 20px;">
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Questions Answered</div>
                <div style="color: #ffffff; font-size: 1.4rem; font-weight: 800; margin-top: 2px;">{results['answered_questions']} / {results['total_questions']}</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Average Score</div>
                <div style="color: #38bdf8; font-size: 1.4rem; font-weight: 800; margin-top: 2px;">{results['average_score']}/100</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Unanswered (Zero Marks)</div>
                <div style="color: {'#fb923c' if results['unanswered_questions'] > 0 else '#4ade80'}; font-size: 1.4rem; font-weight: 800; margin-top: 2px;">{results['unanswered_questions']}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; text-align: center; margin-top: 14px;">
            <div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 10px; padding: 12px;">
                <div style="color: #4ade80; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">🏆 Strongest Skill</div>
                <div style="color: #ffffff; font-size: 1.05rem; font-weight: 700; margin-top: 3px;">{results['strongest_skill']}</div>
            </div>
            <div style="background: rgba(251, 146, 60, 0.08); border: 1px solid rgba(251, 146, 60, 0.25); border-radius: 10px; padding: 12px;">
                <div style="color: #fb923c; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">🎯 Focus Area (Weakest)</div>
                <div style="color: #ffffff; font-size: 1.05rem; font-weight: 700; margin-top: 3px;">{results['weakest_skill']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Detailed Question-by-Question Evaluation Breakdown
    st.subheader("🔍 Detailed Question-by-Question Evaluation")
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.2rem;'>Inspect the rubric breakdown, identified strengths, missing points, areas for improvement, and model answer for each question.</p>", unsafe_allow_html=True)

    for i, ev in enumerate(results["evaluations"]):
        q_sc = ev.get("score", 0)
        q_class = classify_performance(q_sc)
        if q_sc >= 75:
            q_badge_color = "#4ade80"
        elif q_sc >= 50:
            q_badge_color = "#facc15"
        else:
            q_badge_color = "#f87171"

        expander_title = f"Q{i+1}: {ev.get('question')} — [Score: {q_sc}/100 • {q_class}]"
        
        with st.expander(expander_title, expanded=(i == 0)):
            # Metadata Tags
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span class="meta-tag meta-tag-domain">{ev.get('domain', '')}</span>
                <span class="meta-tag meta-tag-skill">{ev.get('skill', '')}</span>
                <span class="meta-tag meta-tag-diff">{ev.get('difficulty', '')}</span>
                <span class="meta-tag meta-tag-type">{ev.get('question_type', '')}</span>
                <span style="display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; color: {q_badge_color}; background: rgba(15, 23, 42, 0.8); border: 1px solid {q_badge_color};">
                    Score: {q_sc}/100
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Criteria Breakdown Grid
            crit = ev.get("criteria_scores", {})
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.88rem; text-transform: uppercase; margin-bottom: 8px;">Scoring Criteria Breakdown:</div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; text-align: center;">
                    <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                        <div style="color: #94a3b8; font-size: 0.75rem;">Correctness</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('technical_correctness', 0)} / 40</div>
                    </div>
                    <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                        <div style="color: #94a3b8; font-size: 0.75rem;">Concepts</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('conceptual_understanding', 0)} / 25</div>
                    </div>
                    <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                        <div style="color: #94a3b8; font-size: 0.75rem;">Relevance</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('relevance', 0)} / 15</div>
                    </div>
                    <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                        <div style="color: #94a3b8; font-size: 0.75rem;">Completeness</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('completeness', 0)} / 15</div>
                    </div>
                    <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                        <div style="color: #94a3b8; font-size: 0.75rem;">Quality</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('explanation_quality', 0)} / 5</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Candidate's Submitted Response
            st.markdown("**Your Submitted Response:**")
            if ev.get("is_unanswered"):
                st.warning("⚠️ *No answer submitted for this question (Score: 0/100)*")
            else:
                st.info(ev.get("candidate_answer", ""))

            # Detailed Feedback Sections
            col_fb1, col_fb2 = st.columns(2)
            with col_fb1:
                st.markdown("<div style='color: #4ade80; font-weight: 700; margin-bottom: 6px;'>✅ What You Did Well:</div>", unsafe_allow_html=True)
                for item in ev.get("what_you_did_well", []):
                    st.write(f"- {item}")

                st.markdown("<div style='color: #fb923c; font-weight: 700; margin-top: 14px; margin-bottom: 6px;'>⚠️ Missing Points:</div>", unsafe_allow_html=True)
                for item in ev.get("missing_points", []):
                    st.write(f"- {item}")

            with col_fb2:
                st.markdown("<div style='color: #38bdf8; font-weight: 700; margin-bottom: 6px;'>💡 Areas to Improve:</div>", unsafe_allow_html=True)
                for item in ev.get("areas_to_improve", []):
                    st.write(f"- {item}")

                st.markdown("<div style='color: #c084fc; font-weight: 700; margin-top: 14px; margin-bottom: 6px;'>📝 Final Assessment:</div>", unsafe_allow_html=True)
                st.markdown(f"*{ev.get('final_evaluation', '')}*")

            # Suggested Model Answer
            st.write("---")
            st.markdown("<div style='color: #7dd3fc; font-weight: 700; font-size: 0.92rem; margin-bottom: 6px;'>📘 Suggested Model Answer:</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.9); border-left: 4px solid #38bdf8; padding: 14px 18px; border-radius: 6px; color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">
                {ev.get('suggested_answer', '')}
            </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # Action Navigation Buttons
    col_b1, col_b2, col_b3 = st.columns([1.4, 1.2, 1])
    with col_b1:
        if st.button("Practice Another Topic", key="btn_practice_again", type="primary", use_container_width=True):
            st.session_state.current_page = 'technical_setup'
            st.rerun()
    with col_b2:
        if st.button("Mode Selection", key="btn_return_mode_from_analysis", type="secondary", use_container_width=True):
            st.session_state.current_page = 'mode_selection'
            st.rerun()
    with col_b3:
        if st.button("Home", key="btn_return_home_from_analysis", type="secondary", use_container_width=True):
            st.session_state.current_page = 'landing'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_interview_page():
    if st.button("← Go to Home", type="secondary"):
        st.session_state.current_page = 'landing'
        st.rerun()
        return

    # Show Simulation Mode Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge">🔴 Real-Time Interview Simulation Mode</div></div>', unsafe_allow_html=True)
    
    # If we have reached the end of the questions
    if st.session_state.question_index >= len(st.session_state.current_questions):
        st.session_state.current_page = 'results'
        st.rerun()
        return

    # 1. STRICT READINESS CHECK (BEFORE QUESTION IS DISPLAYED)
    if st.session_state.question_index == 0 and not st.session_state.hardware_verified:
        st.info("🔄 Checking Camera & Microphone Readiness...")
        
        # Explicitly trigger browser permissions via JS to mimic "the site asking"
        components.html(
            """
            <script>
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then((stream) => {
                stream.getTracks().forEach(track => track.stop());
            })
            .catch((err) => {
                console.log("Permission denied: ", err);
            });
            </script>
            """,
            height=0,
            width=0,
        )
        
        # Brief check to ensure cv2 can open and microphone is accessible. Add retries.
        hardware_ready = False
        for attempt in range(3):
            try:
                cam_ready = False
                mic_ready = False
                
                # Check Camera
                test_cap = get_camera()
                if test_cap is not None:
                    ret, _ = test_cap.read()
                    test_cap.release()
                    if ret:
                        cam_ready = True

                # Check Microphone
                try:
                    with sr.Microphone() as source:
                        mic_ready = True
                except Exception as e:
                    print(f"Microphone test failed: {e}")
                    mic_ready = False
                    
                if cam_ready and mic_ready:
                    hardware_ready = True
                    break
            except Exception:
                pass
            time.sleep(1.0)
            
        if not hardware_ready:
            st.error("❌ Camera/Microphone access denied or hardware not found.\n\nPlease click the site settings icon (🔒) in your browser URL bar to 'Allow' access to Camera and Microphone, or check your OS privacy settings.")
            if st.button("Retry Access", type="primary"):
                st.rerun()
            return # Halt rendering until fixed
            
        st.success("✅ Camera & Microphone Ready!")
        time.sleep(1.5)
        st.session_state.hardware_verified = True
        st.rerun() # Rerun to cleanly start the question
        return

    current_q = st.session_state.current_questions[st.session_state.question_index]
    total_q = len(st.session_state.current_questions)
    current_q_num = st.session_state.question_index + 1
    
    # Display Progress Indicator
    st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 0.5rem;'>Question {current_q_num} of {total_q}</div>", unsafe_allow_html=True)
    st.progress(current_q_num / total_q)
    
    # Display the current question with custom styling
    st.markdown(f'<div class="question-text">Q{current_q_num}: {current_q}</div>', unsafe_allow_html=True)

    # Speak the question automatically only once per question
    if not st.session_state.question_spoken:
        speak_question(current_q)
        st.session_state.question_spoken = True

    if not st.session_state.is_recording and not st.session_state.analysis_done:
        countdown_placeholder = st.empty()
        
        # Show countdown visually
        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"<h2 style='text-align: center; color: #facc15;'>Starting in {i}...</h2>", unsafe_allow_html=True)
            time.sleep(1)
            
        countdown_placeholder.empty()
        
        # Start recording
        st.session_state.is_recording = True
        st.session_state.frames = []
        st.rerun()
            
    elif st.session_state.is_recording:
        st.write("🎙️ Recording your response...")
        camera_placeholder = st.empty()
        timer_placeholder = st.empty()
        
        record_duration = get_question_duration(current_q)
        
        # Start background audio thread
        audio_result = []
        audio_thread = threading.Thread(target=record_and_transcribe, args=(record_duration, audio_result))
        audio_thread.start()
        
        # Start camera
        camera = get_camera()
        if camera is None:
            camera_placeholder.error("Failed to access webcam.")
            st.session_state.is_recording = False
            return

        start_time = time.time()
        
        while time.time() - start_time < record_duration:
            ret, frame = camera.read()
            if not ret:
                camera_placeholder.error("Webcam disconnected.")
                break
                
            # Convert BGR to RGB for Streamlit
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display live feed
            camera_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)
            
            # Sample frame 1 per second
            elapsed = time.time() - start_time
            if int(elapsed) >= len(st.session_state.frames):
                st.session_state.frames.append(rgb_frame)
                
            # Update timer UI
            remaining = int(record_duration - elapsed)
            timer_placeholder.markdown(f"<h3 style='text-align: center; color: #ffeb3b;'>⏳ Time Remaining: {remaining}s</h3>", unsafe_allow_html=True)
            
        # Loop finished
        camera.release()
        camera_placeholder.empty()
        timer_placeholder.empty()
        
        with st.spinner("Analyzing your response..."):
            # Wait for audio to finish
            audio_thread.join()
            transcribed_text = audio_result[0] if audio_result else ""
            
            # Check for explicitly caught errors
            if transcribed_text.startswith("ERROR:"):
                st.session_state.last_audio_error = transcribed_text
                transcribed_text = ""
            else:
                st.session_state.last_audio_error = None
            
            # Process frames
            video_res = aggregate_video_analysis(st.session_state.frames)
            st.session_state.video_results.append(video_res)
            
            # Process Audio
            audio_res = analyze_audio_behavior(transcribed_text, record_duration)
            st.session_state.audio_results.append(audio_res)
            
        st.session_state.is_recording = False
        st.session_state.analysis_done = True
        st.rerun()

    elif st.session_state.analysis_done:
        st.success("Analysis Complete for this question!")
        
        # Display audio validation warning if no speech detected
        last_audio_res = st.session_state.audio_results[-1]
        if st.session_state.last_audio_error:
            st.error(f"🎙️ Audio Issue: {st.session_state.last_audio_error}\n\nPlease check your microphone settings or ensure you have a working internet connection.")
        elif not last_audio_res.get("meaningful", True):
            st.warning("⚠️ No speech detected. Please speak clearly into your microphone.")
        
        is_last_question = st.session_state.question_index == len(st.session_state.current_questions) - 1
        
        if is_last_question:
            if st.button("View Final Report", type="primary", use_container_width=True):
                st.session_state.question_index += 1
                st.session_state.question_spoken = False
                st.session_state.is_recording = False
                st.session_state.analysis_done = False
                st.session_state.frames = []
                st.rerun()
        else:
            # Auto-transition to next question
            st.info("Moving to the next question shortly...")
            time.sleep(2)
            st.session_state.question_index += 1
            st.session_state.question_spoken = False
            st.session_state.is_recording = False
            st.session_state.analysis_done = False
            st.session_state.frames = []
            st.rerun()

def render_results_page():
    st.title("📊 Final Interview Verdict")
    st.write("Here is the analysis of your performance based on behavioral and simulated speech metrics.")
    st.write("---")

    # Calculate final scores
    scores = calculate_scores(st.session_state.video_results, st.session_state.audio_results)
    
    # Display Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence Score", f"{scores['confidence']}/100")
    with col2:
        st.metric("Nervousness Index", f"{scores['nervousness']}/100")
    with col3:
        st.metric("Communication Score", f"{scores['communication']}/100")

    st.write("---")
    
    # Generate Feedback
    feedback = generate_feedback(scores)
    
    # Display Verdict
    st.markdown(f"### Final Verdict: <span class='{feedback['verdict_class']}'>{feedback['verdict']} { '✅' if 'Ready' in feedback['verdict'] else '⚠️' if 'Improvement' in feedback['verdict'] else '❌' }</span>", unsafe_allow_html=True)
    st.markdown(f"**Overall Score:** {feedback['overall_score']}/100")

    st.write("---")
    st.subheader("💡 Detailed Feedback")
    
    colA, colB, colC = st.columns(3)
    
    with colA:
        st.success("**Strengths**")
        for item in feedback["positive"]:
            st.write(f"- {item}")
            
    with colB:
        st.warning("**Areas to Improve**")
        for item in feedback["improvement"]:
            st.write(f"- {item}")
            
    with colC:
        st.error("**Critical Issues**")
        if len(feedback["negative"]) > 0:
            for item in feedback["negative"]:
                st.write(f"- {item}")
        else:
            st.write("- None detected. Great job!")

    st.write("---")
    if st.button("Restart Interview", type="primary", use_container_width=True):
        st.session_state.current_page = 'landing'
        st.rerun()

def main():
    apply_css()
    init_session_state()

    # Simple router
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'mode_selection':
        render_mode_selection_page()
    elif st.session_state.current_page == 'technical_setup':
        render_technical_setup_page()
    elif st.session_state.current_page == 'technical_interview':
        render_technical_interview_page()
    elif st.session_state.current_page in ('technical_submission', 'technical_completed'):
        render_technical_submission_page()
    elif st.session_state.current_page in ('technical_analysis', 'technical_analysis_placeholder'):
        render_technical_analysis_page()
    elif st.session_state.current_page == 'interview':
        render_interview_page()
    elif st.session_state.current_page == 'results':
        render_results_page()

if __name__ == "__main__":
    main()
