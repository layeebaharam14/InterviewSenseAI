import streamlit as st
import streamlit.components.v1 as components
import cv2
import time
import threading
import speech_recognition as sr
import re
import uuid
from datetime import datetime

from src.interviewsense.utils.styling import scroll_to_top, apply_css, speak_question
from src.interviewsense.analysis.video_analysis import (
    aggregate_video_analysis,
    analyze_technical_question_frames,
    calculate_overall_visual_analysis,
)
from src.interviewsense.analysis.audio_analysis import analyze_audio_behavior
from src.interviewsense.core.scoring import calculate_scores
from src.interviewsense.core.insights import generate_feedback
from src.interviewsense.data.technical_questions import generate_technical_questions
from src.interviewsense.analysis.technical_evaluation import (
    evaluate_technical_interview,
    evaluate_technical_answer,
    classify_performance,
    generate_combined_summary,
    generate_improvement_roadmap,
)
from src.interviewsense.reports.technical_report_pdf import generate_technical_pdf_report
from src.interviewsense.services.technical_speech import (
    normalize_technical_terms,
    record_and_transcribe_audio,
    transcribe_audio_file,
    get_temp_audio_path,
    cleanup_temp_audio,
)
import pandas as pd

# Local helpers (shared across UI modules via app_helpers)
from src.interviewsense.core.app_helpers import (
    QUESTION_POOL,
    get_question_duration,
    get_technical_question_duration,
    get_camera,
    record_and_transcribe,
    record_technical_voice_answer,
    save_current_technical_answer,
)


def render_landing_page():
    st.markdown('<div id="top-anchor"></div><div id="landing-page-marker"></div>', unsafe_allow_html=True)
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
/* Force container backgrounds to be transparent on home */
.block-container, .main, [data-testid="stHeader"] {
    background: transparent !important;
    background-color: transparent !important;
}
/* Collapse empty marker containers so they do not add unwanted vertical gap */
div[data-testid="stElementContainer"]:has(#top-anchor),
div[data-testid="stElementContainer"]:has(#landing-page-marker),
div[data-testid="stElementContainer"]:has(#home-bg-injector) {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* Ensure fixed navbar container wrapper takes 0 flow height */
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    position: absolute !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* Full viewport layout for Home tab offset by top navbar */
[data-testid="stMainBlockContainer"]:has(.st-key-home_hero),
.block-container:has(.st-key-home_hero),
section[data-testid="stMain"]:has(.st-key-home_hero) [data-testid="stMainBlockContainer"],
body:has(.st-key-home_hero) [data-testid="stMainBlockContainer"],
body:has(.st-key-home_hero) .block-container,
body:has(#home-bg-injector) [data-testid="stMainBlockContainer"],
body:has(#home-bg-injector) .block-container {
    padding-top: 3.4rem !important;
    padding-bottom: 0 !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    height: 100vh !important;
    height: 100dvh !important;
    min-height: 100vh !important;
    min-height: 100dvh !important;
    max-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    box-sizing: border-box !important;
}
/* Parent vertical block on Home stretches and centers content without gap */
[data-testid="stMainBlockContainer"]:has(.st-key-home_hero) > div[data-testid="stVerticalBlock"],
.block-container:has(.st-key-home_hero) > div[data-testid="stVerticalBlock"],
body:has(#home-bg-injector) [data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"],
body:has(#home-bg-injector) .block-container > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    height: 100% !important;
}
/* Homepage Hero Centered Flex Container */
div[data-testid="stLayoutWrapper"]:has(.st-key-home_hero),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-home_hero),
.st-key-home_hero {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: calc(100vh - 3.4rem) !important;
    min-height: calc(100dvh - 3.4rem) !important;
    width: 100% !important;
    margin: 0 auto !important;
    box-sizing: border-box !important;
}
.st-key-home_hero {
    max-width: 800px !important;
}
.st-key-home_hero > div[data-testid="stElementContainer"] {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
.st-key-home_hero > div[data-testid="stElementContainer"] > div {
    width: 100% !important;
    text-align: center !important;
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
        
        with st.container(key="home_hero"):
            st.title("🎯 InterviewSense AI")
            st.subheader("Real-Time Interview Performance Analyzer")
            st.write("Simulate a real interview environment. We will ask you questions, analyze your behavioral responses via webcam, and provide detailed feedback.")
            st.write("---")
            
            if st.button("Start Interview", type="primary", use_container_width=True):
                st.session_state.current_page = 'mode_selection'
                scroll_to_top()
                st.rerun()

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

        div[data-testid="stColumns"]:has([class^="marker-"]), div[data-testid="stHorizontalBlock"]:has([class^="marker-"]) {
            margin-bottom: 14px !important;
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
        st.markdown("<h2 class='section-title' style='margin-top: 0; margin-bottom: 1.2rem;'>About InterviewSense AI</h2>", unsafe_allow_html=True)
        
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
            
        # Spacing handled cleanly via card margins
        
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
            
        # Spacing handled cleanly via card margins
        
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
        
        # Spacing handled cleanly via card margins
        
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
        
        # Spacing handled cleanly via card margins
        
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
        # GUIDELINES SECTION - CLEAN RAW HTML (NO CODE BLOCK INTERPRETATION)
        st.markdown('''<div class="page-section" style="max-width: 1200px; margin: 0 auto;">
<div style="text-align: center; margin-bottom: 2.5rem;">
<h2 class="section-title" style="margin-bottom: 0.5rem;">Interview Guidelines &amp; Best Practices</h2>
<p style="color: #94a3b8; font-size: 1.1rem; max-width: 800px; margin: 0 auto; line-height: 1.6;">Master your technical and behavioral interviews with InterviewSense AI. Follow these structured guidelines, operational workflows, and proven frameworks to maximize your score and interview readiness.</p>
</div>
<div class="guidelines-grid">
<div class="guideline-card">
<span class="guideline-badge">Modes &amp; Selection</span>
<div class="guideline-title">🎯 1. Interview Modes</div>
<ul class="guideline-points">
<li><strong>Mock HR Interview:</strong> Behavioral simulation evaluating soft skills, communication clarity, situational answers (STAR method), and interpersonal presence.</li>
<li><strong>Technical Interview:</strong> Real-time technical assessment measuring conceptual depth, system architecture, problem-solving, and domain terminology.</li>
<li><strong>Targeted Preparation:</strong> Select the mode matching your upcoming interview requirements or alternate between both for complete readiness.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Configuration</span>
<div class="guideline-title">⚙️ 2. Domain &amp; Skill Setup</div>
<ul class="guideline-points">
<li><strong>Engineering Domains:</strong> Choose from 10+ core domains including Frontend, Backend, AI/ML, DevOps, Cloud Architecture, and Data Engineering.</li>
<li><strong>Skill Targeting:</strong> Toggle key skills (Python, Docker, React, PyTorch, Kubernetes) to customize the question pool to your expertise.</li>
<li><strong>Difficulty &amp; Length:</strong> Set your target seniority level (Beginner, Intermediate, Advanced) and select 3 to 10 questions for tailored interview duration.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Pre-Interview</span>
<div class="guideline-title">🎙️ 3. Hardware &amp; Environment</div>
<ul class="guideline-points">
<li><strong>Camera Positioning:</strong> Center your webcam at eye level with balanced front lighting. Avoid strong backlights or dark shadows across your face.</li>
<li><strong>Microphone Setup:</strong> Use a stable USB or headset microphone in a quiet room free of echo, background music, or keyboard clicks.</li>
<li><strong>Permission Check:</strong> Grant browser camera and mic access when prompted. The setup screen provides instant hardware verification before starting.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Execution</span>
<div class="guideline-title">⏱️ 4. Technical Flow &amp; Timers</div>
<ul class="guideline-points">
<li><strong>Question Playback:</strong> The AI speaks each question aloud using text-to-speech. Listen carefully without speaking during playback.</li>
<li><strong>3-Second Countdown:</strong> A visible 3-second preparation countdown (3... 2... 1...) appears immediately after question audio finishes.</li>
<li><strong>Automatic Camera &amp; Mic:</strong> Hardware activates automatically at countdown zero — no manual click required.</li>
<li><strong>Fixed 15-Second Recording:</strong> Deliver a concise, focused answer within the fixed 15-second response window. Recording stops automatically.</li>
<li><strong>Seamless Progression:</strong> Your audio and visual frames are preserved, and the system automatically advances to the subsequent question.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Framework</span>
<div class="guideline-title">💡 5. Answering Framework (DMET)</div>
<ul class="guideline-points">
<li><strong>Definition (D):</strong> Begin with a crisp, 1-sentence formal definition of the concept or pattern.</li>
<li><strong>Mechanics (M):</strong> Explain how it works internally — data structures, control flow, memory layout, or architectural components.</li>
<li><strong>Example (E):</strong> Reference a concrete production use case, code pattern, or real-world system scenario.</li>
<li><strong>Trade-offs (T):</strong> Highlight computational complexity, edge cases, scalability bottlenecks, or alternative design approaches.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Review &amp; Polish</span>
<div class="guideline-title">📝 6. Speech Capture &amp; Review</div>
<ul class="guideline-points">
<li><strong>Technical STT Engine:</strong> Speech recognition incorporates engineering domain dictionaries to reliably capture specialized terminology.</li>
<li><strong>Submission Review Screen:</strong> After completing all questions, you are directed to a dedicated review page displaying your transcribed responses.</li>
<li><strong>Transcript Editing:</strong> Review and refine any speech-to-text transcript before final AI submission to ensure your answers accurately reflect your intent.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Evaluation</span>
<div class="guideline-title">📊 7. 100-Point Scoring Rubric</div>
<ul class="guideline-points">
<li><strong>Technical Accuracy &amp; Depth (30 pts):</strong> Factual correctness, precision of concepts, and domain mastery.</li>
<li><strong>Completeness &amp; Trade-offs (25 pts):</strong> Coverage of edge cases, architectural trade-offs, and system constraints.</li>
<li><strong>Communication &amp; Terminology (20 pts):</strong> Articulation, concise phrasing, and appropriate use of technical vocabulary.</li>
<li><strong>Problem-Solving Structure (15 pts):</strong> Methodical breakdown, structured reasoning, and logical progression.</li>
<li><strong>Visual Presence (10 pts):</strong> Camera engagement, consistent posture, and professional composure.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Ethics &amp; Privacy</span>
<div class="guideline-title">👁️ 8. Visual Telemetry &amp; Privacy</div>
<ul class="guideline-points">
<li><strong>Engagement Tracking:</strong> OpenCV and MediaPipe estimate face presence and camera-facing gaze to provide constructive engagement metrics.</li>
<li><strong>Posture Estimation:</strong> Head pose orientation and upper-body posture are measured to encourage confident, upright presence.</li>
<li><strong>100% In-Memory Processing:</strong> Camera frames and audio streams are processed in temporary session memory and are never uploaded, sold, or stored permanently.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Reporting</span>
<div class="guideline-title">📑 9. Analytics &amp; PDF Export</div>
<ul class="guideline-points">
<li><strong>Multi-Dimensional Dashboards:</strong> View overall score gauges, performance tiers, category radars, and per-question rubrics.</li>
<li><strong>Detailed Question Feedback:</strong> Inspect model answers, key strengths, and specific areas for technical growth for every answered question.</li>
<li><strong>One-Click PDF Report:</strong> Generate and download a formatted interview evaluation report for offline progress tracking and interview logs.</li>
</ul>
</div>
<div class="guideline-card">
<span class="guideline-badge">Troubleshooting</span>
<div class="guideline-title">🛠️ 10. Troubleshooting &amp; Support</div>
<ul class="guideline-points">
<li><strong>Camera Access Denied:</strong> Ensure no other application (Zoom, Teams) is using the webcam, and confirm browser permissions are allowed.</li>
<li><strong>Microphone Recognition:</strong> Speak at an even pace and conversational volume; avoid long silence at the beginning of the 15-second window.</li>
<li><strong>Navigation &amp; Scroll:</strong> Click any navbar tab (Home, About, Features, Guidelines) to instantly jump to that section at the top of the page.</li>
</ul>
</div>
</div>
<div style="text-align: center; margin-top: 3rem; margin-bottom: 1.5rem;">
<div style="display: inline-block; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 1.25rem 2.5rem;">
<span style="color: #38bdf8; font-size: 1.1rem; font-weight: 700;">Ready to put these guidelines into action?</span>
<div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.4rem;">Click "Home" on the navigation bar above and press "Start Interview" to begin.</div>
</div>
</div>
</div>''', unsafe_allow_html=True)

