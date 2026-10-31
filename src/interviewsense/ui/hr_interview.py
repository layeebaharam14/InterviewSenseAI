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


def render_interview_page():

    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    if st.button("← Go to Home", type="secondary"):
        st.session_state.current_page = 'landing'
        st.session_state.current_tab = 'Home'
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
            col_hw1, col_hw2 = st.columns(2)
            with col_hw1:
                if st.button("Retry Access", key="btn_retry_hw_acc", type="primary", use_container_width=True):
                    st.rerun()
            with col_hw2:
                if st.button("Continue in Demo / Simulation Mode", key="btn_bypass_hw_acc", type="secondary", use_container_width=True):
                    st.session_state.hardware_verified = True
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
            
            # Rate limit frame updates to ~25 fps to prevent Streamlit MediaFileStorageError
            time.sleep(0.04)
            
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

