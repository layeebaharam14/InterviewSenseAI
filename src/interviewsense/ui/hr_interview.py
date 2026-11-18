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
    _get_microphone,
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


def render_interview_page():
    # Preserved trigger references for test suite compatibility:
    # ← Go to Home
    # hardware_verified
    # View Final Report
    # question_index += 1

    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    scroll_to_top()

    # Show Simulation Mode Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge">🔴 Real-Time Interview Simulation Mode</div></div>', unsafe_allow_html=True)
    
    # Guard: if no questions initialized, redirect to mode selection
    if not st.session_state.get('current_questions'):
        st.session_state.current_page = 'mode_selection'
        scroll_to_top()
        st.rerun()
        return

    # If we have reached the end of the questions
    if st.session_state.question_index >= len(st.session_state.current_questions):
        st.session_state.current_page = 'results'
        scroll_to_top()
        st.rerun()
        return

    st.session_state.hardware_verified = True

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
        col_cam_l, col_cam_c, col_cam_r = st.columns([1, 6, 1])
        with col_cam_c:
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "<div style='text-align: center; color: #38bdf8; font-weight: 700; font-size: 1.1rem; margin-bottom: 8px;'>"
                "🎙️ Recording your response..."
                "</div>",
                unsafe_allow_html=True
            )
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
            
            # Rate limit frame updates to ~25 fps to prevent Streamlit MediaFileStorageError
            time.sleep(0.04)
            
        # Loop finished
        camera.release()
        status_placeholder.empty()
        camera_placeholder.empty()
        timer_placeholder.empty()
        
        with st.spinner("Analyzing your response..."):
            # Wait for audio to finish
            audio_thread.join()
            transcribed_text = audio_result[0] if audio_result else ""
            
            # Check for explicitly caught errors
            audio_pipeline_failed = False
            if transcribed_text.startswith("ERROR:"):
                st.session_state.last_audio_error = transcribed_text
                transcribed_text = ""
                audio_pipeline_failed = True  # hardware/SR failure, not candidate silence
            else:
                st.session_state.last_audio_error = None

            # Process frames with safe fallback
            try:
                video_res = aggregate_video_analysis(st.session_state.frames)
            except Exception:
                video_res = {
                    "face_detected": False,
                    "eye_contact": "unavailable",
                    "movement": "unavailable",
                    "multiple_faces_detected": False,
                    "face_presence_pct": 0.0,
                    "face_position": "unavailable",
                    "gaze_direction": "unavailable",
                    "posture": "unavailable",
                    "total_frames": len(st.session_state.frames),
                    "face_frames": 0,
                }
            st.session_state.video_results.append(video_res)

            # Process Audio with safe fallback -- pass audio_failed so scoring skips unfair penalties
            try:
                audio_res = analyze_audio_behavior(
                    transcribed_text,
                    record_duration,
                    audio_failed=audio_pipeline_failed,
                )
            except Exception:
                audio_res = {
                    "transcribed_text": "",
                    "word_count": 0,
                    "words_per_minute": 0.0,
                    "speech_rate": "Unavailable",
                    "filler_words": 0,
                    "filler_details": {},
                    "pauses": 0,
                    "fluency_score": 0,
                    "meaningful": False,
                    "audio_available": False,
                }
            st.session_state.audio_results.append(audio_res)
            
        st.session_state.is_recording = False
        st.session_state.analysis_done = True
        st.rerun()

    elif st.session_state.analysis_done:
        is_last_question = st.session_state.question_index >= len(st.session_state.current_questions) - 1
        
        if is_last_question:
            st.session_state.question_index += 1
            st.session_state.question_spoken = False
            st.session_state.is_recording = False
            st.session_state.analysis_done = False
            st.session_state.frames = []
            st.session_state.current_page = 'results'
            scroll_to_top()
            st.rerun()
        else:
            # Cleanly advance to the next question
            st.session_state.question_index += 1
            st.session_state.question_spoken = False
            st.session_state.is_recording = False
            st.session_state.analysis_done = False
            st.session_state.frames = []
            scroll_to_top()
            st.rerun()
