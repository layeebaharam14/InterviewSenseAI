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


def render_results_page():

    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
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
        st.session_state.current_tab = 'Home'
        st.rerun()

