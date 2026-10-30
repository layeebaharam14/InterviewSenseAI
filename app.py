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

def render_technical_setup_page():
    """Placeholder page for Step 2 - Technical Interview Setup."""
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Modes", key="back_to_modes_btn", type="secondary"):
            st.session_state.current_page = 'mode_selection'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.5rem;">', unsafe_allow_html=True)
    st.title("💻 Technical Interview Setup")
    st.subheader("Configure your technical domain and practice preferences.")
    st.write("---")

    st.markdown("""
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 36px; text-align: center; max-width: 650px; margin: 2rem auto; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);">
        <div style="font-size: 3.5rem; margin-bottom: 1rem;">⚙️</div>
        <h3 style="color: #38bdf8; margin-bottom: 0.8rem;">Technical Setup In Progress</h3>
        <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1.5rem;">
            Domain and skill selection options will be configured here in <strong>Step 2</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("Return to Mode Selection", key="return_mode_center_btn", type="primary", use_container_width=True):
            st.session_state.current_page = 'mode_selection'
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
    elif st.session_state.current_page == 'interview':
        render_interview_page()
    elif st.session_state.current_page == 'results':
        render_results_page()

if __name__ == "__main__":
    main()
