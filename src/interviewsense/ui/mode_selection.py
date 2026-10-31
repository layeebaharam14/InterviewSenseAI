import streamlit as st
import random
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
    TECHNICAL_DOMAIN_SKILLS,
    QUESTION_POOL,
    get_question_duration,
    get_technical_question_duration,
    get_camera,
    record_and_transcribe,
    record_technical_voice_answer,
    save_current_technical_answer,
)


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
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Home", key="back_to_home_mode", type="secondary"):
            st.session_state.current_page = 'landing'
            st.session_state.current_tab = 'Home'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
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
