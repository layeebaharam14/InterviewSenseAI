import streamlit as st
import streamlit.components.v1 as components
import cv2
import time
import threading
import speech_recognition as sr
import re
import uuid
from datetime import datetime

from src.interviewsense.utils.styling import scroll_to_top, apply_css, speak_question, render_html
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
    TECHNICAL_DOMAIN_SKILLS,
    get_question_duration,
    get_technical_question_duration,
    get_camera,
    record_and_transcribe,
    record_technical_voice_answer,
    save_current_technical_answer,
)


def render_technical_interview_page():
    """Renders the Step 3 Live Interactive Technical Interview Page with fixed 15s question flow."""
    if st.session_state.get('current_page') != 'technical_interview':
        return

    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    scroll_to_top()

    if not st.session_state.technical_questions:
        st.session_state.current_page = 'technical_setup'
        st.rerun()
        return

    total_q = len(st.session_state.technical_questions)
    curr_idx = st.session_state.technical_question_index

    # Check if all questions are completed
    if curr_idx >= total_q:
        st.session_state.technical_interview_completed = True
        st.session_state.technical_interview_submitted = True
        st.session_state.current_page = 'technical_submission'
        st.rerun()
        return

    # Hardware verification check before Question 1
    if curr_idx == 0 and not st.session_state.technical_hardware_verified:
        st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
        st.title("📹 Camera & Microphone Verification")
        st.subheader("Verifying your camera and microphone readiness for the live technical interview.")

        components.html(
            """
            <script>
            navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then((stream) => { stream.getTracks().forEach(track => track.stop()); })
            .catch((err) => { console.log("Permission denied: ", err); });
            </script>
            """,
            height=0, width=0
        )

        with st.spinner("Testing camera and microphone hardware..."):
            cam_ready = False
            mic_ready = False
            test_cap = get_camera()
            if test_cap is not None:
                ret, _ = test_cap.read()
                test_cap.release()
                if ret:
                    cam_ready = True
            try:
                with sr.Microphone() as source:
                    mic_ready = True
            except Exception:
                mic_ready = False

        if cam_ready and mic_ready:
            st.success("✅ Camera and Microphone Ready! Proceeding to interview...")
            time.sleep(1.0)
            st.session_state.technical_hardware_verified = True
            scroll_to_top()
            st.rerun()
            return
        else:
            st.error("❌ Camera or Microphone access was not detected or is currently in use.")
            c_retry, c_sim = st.columns(2)
            with c_retry:
                if st.button("🔄 Retry Access Check", key="btn_retry_tech_hw", type="primary", use_container_width=True):
                    st.rerun()
            with c_sim:
                if st.button("Continue in Demo / Simulation Mode", key="btn_sim_tech_hw", type="secondary", use_container_width=True):
                    st.session_state.technical_hardware_verified = True
                    scroll_to_top()
                    st.rerun()
            return

    curr_q_num = curr_idx + 1
    curr_q_data = st.session_state.technical_questions[curr_idx]
    record_duration = 15  # Exactly 15-second fixed timer for all questions
    st.session_state.technical_recording_duration = record_duration

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
            scroll_to_top()
            st.rerun()
            return
    with col_t2:
        render_html(f"""
        <div style="text-align: right; padding-top: 6px;">
            <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.35); padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; margin-right: 8px;">
                ✅ Answered: {answered_count}/{total_q}
            </span>
            <span style="background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.35); padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">
                ⏳ Unanswered: {unanswered_count}
            </span>
        </div>
        """)

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)

    # Simulation Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge" style="background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.4); color: #7dd3fc;">⚡ Live Real-Time Technical Interview</div></div>', unsafe_allow_html=True)

    st.title("💻 Technical Interview")

    # Progress Display
    st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 0.5rem;'>Question <strong>{curr_q_num}</strong> of <strong>{total_q}</strong></div>", unsafe_allow_html=True)
    st.progress(curr_q_num / total_q)

    # Scoped styling
    render_html("""
    <style>
    .tech-question-card {
        background: linear-gradient(145deg, #0b1120, #0f172a);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 18px 20px;
        margin: 0.5rem auto 0.8rem auto;
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
        margin-bottom: 10px;
    }
    .meta-tag-domain { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .meta-tag-skill { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .meta-tag-diff { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .meta-tag-type { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .tech-q-text {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        line-height: 1.5;
        margin-top: 8px;
        margin-bottom: 6px;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
    }
    </style>
    """)

    # Question metadata & Text
    q_domain = curr_q_data.get("domain", st.session_state.technical_domain)
    q_skill = curr_q_data.get("skill", "General")
    q_diff = curr_q_data.get("difficulty", st.session_state.technical_difficulty)
    q_type = curr_q_data.get("question_type", "Conceptual")
    q_text = curr_q_data.get("question", "")

    render_html(f"""
    <div class="tech-question-card">
        <div>
            <span class="meta-tag meta-tag-domain">{q_domain}</span>
            <span class="meta-tag meta-tag-skill">{q_skill}</span>
            <span class="meta-tag meta-tag-diff">{q_diff}</span>
            <span class="meta-tag meta-tag-type">{q_type}</span>
            <span class="meta-tag" style="background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.3);">⏱️ 15s Fixed Duration</span>
        </div>
        <div class="tech-q-text">
            Q{curr_q_num}: {q_text}
        </div>
    </div>
    """)

    # Stable, fixed layout placeholders in consistent vertical order:
    # 1. Stage status banner
    stage_status_placeholder = st.empty()

    # 2. Centered camera viewport slot
    col_cam_l, col_cam_c, col_cam_r = st.columns([1, 6, 1])
    with col_cam_c:
        camera_placeholder = st.empty()

    # 3. Timer & guidance banner
    timer_placeholder = st.empty()

    # =========================================================================
    # STAGE 1: DISPLAY QUESTION & SPEAK AUDIO COMPLETELY
    # =========================================================================
    spoken_key = f"tech_spoken_{curr_idx}"
    if not st.session_state.get(spoken_key, False):
        # Set spoken flag FIRST to prevent duplicate executions
        st.session_state[spoken_key] = True

        stage_status_placeholder.markdown("""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 14px 20px; margin: 8px 0; text-align: center;">
            <p style="color: #38bdf8; font-size: 1.1rem; font-weight: 700; margin-bottom: 4px;">
                🔊 Speaking Question... Please listen carefully.
            </p>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0;">
                Camera and microphone remain inactive until audio playback finishes.
            </p>
        </div>
        """, unsafe_allow_html=True)

        camera_placeholder.markdown("""
        <div class="camera-standby-box">
            <div style="font-size: 3rem; margin-bottom: 10px;">📹</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #38bdf8; margin-bottom: 6px;">
                Camera & Microphone Standby
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8;">
                Listening to question audio. Recording begins after the 3-second countdown.
            </div>
        </div>
        """, unsafe_allow_html=True)

        timer_placeholder.markdown("""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 10px 20px; text-align: center;">
            <span style="color: #94a3b8; font-size: 0.9rem;">⏳ 15-second recording timer will start after question audio and countdown.</span>
        </div>
        """, unsafe_allow_html=True)

        audio_duration = speak_question(q_text)
        time.sleep(audio_duration + 0.3)

    # =========================================================================
    # STAGE 2: EXACT THREE-SECOND COUNTDOWN (CAMERA & MIC INACTIVE)
    # =========================================================================
    countdown_key = f"tech_countdown_done_{curr_idx}"
    if not st.session_state.get(countdown_key, False):
        stage_status_placeholder.markdown("""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(250, 204, 21, 0.3); border-radius: 12px; padding: 12px 20px; margin: 8px 0; text-align: center;">
            <span style="color: #facc15; font-size: 1.05rem; font-weight: 700;">
                ⏳ Preparing response recording...
            </span>
        </div>
        """, unsafe_allow_html=True)

        for count in (3, 2, 1):
            camera_placeholder.markdown(f"""
            <div class="camera-standby-box" style="border-color: rgba(250, 204, 21, 0.5);">
                <div style="font-size: 4.5rem; font-weight: 900; color: #facc15; text-shadow: 0 0 25px rgba(250, 204, 21, 0.6); line-height: 1;">
                    {count}
                </div>
                <div style="font-size: 1.2rem; color: #ffffff; font-weight: 700; margin-top: 12px;">
                    Get Ready to Answer
                </div>
                <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 4px;">
                    Camera and microphone will activate automatically in {count}s.
                </div>
            </div>
            """, unsafe_allow_html=True)

            timer_placeholder.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(250, 204, 21, 0.2); border-radius: 12px; padding: 10px 20px; text-align: center;">
                <span style="color: #facc15; font-size: 0.95rem; font-weight: 600;">Starting in {count}...</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1.0)

        st.session_state[countdown_key] = True

    # =========================================================================
    # STAGE 3 & 4: AUTOMATIC CAMERA & MICROPHONE ACTIVATION (FIXED 15s TIMER)
    # =========================================================================
    stage_status_placeholder.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin: 8px 0 12px 0;">
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 10px #ef4444;"></span>
        <span style="color: #ef4444; font-weight: 800; font-size: 1.1rem; letter-spacing: 0.5px;">🔴 LIVE RECORDING IN PROGRESS — 15 SECONDS</span>
    </div>
    """, unsafe_allow_html=True)

    # Prepare temporary audio file for recovery
    audio_path = get_temp_audio_path(st.session_state.technical_session_id, curr_idx)
    st.session_state.technical_audio_files[curr_idx] = audio_path

    # Activate microphone recording concurrently in background thread with technical context
    audio_result = []
    audio_thread = threading.Thread(
        target=record_and_transcribe,
        args=(15, audio_result, q_domain, [q_skill], audio_path)
    )
    audio_thread.start()

    # Activate camera preview
    camera = get_camera()
    if camera is None:
        camera_placeholder.warning("⚠️ Webcam could not be accessed. Recording your audio response...")

    start_time = time.time()
    sampled_frames = []

    while time.time() - start_time < 15.0:
        elapsed = time.time() - start_time
        remaining = max(0, int(15.0 - elapsed))

        if camera is not None:
            ret, frame = camera.read()
            if not ret:
                camera.release()
                camera = None
                camera_placeholder.warning("⚠️ Webcam feed interrupted. Continuing to record audio response...")
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                camera_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

                # Sample 1 frame per second for MediaPipe facial & behavioral analysis
                if int(elapsed) >= len(sampled_frames):
                    sampled_frames.append(rgb_frame)

        # Update countdown display (15 down to 0)
        timer_color = "#4ade80" if remaining > 7 else ("#facc15" if remaining > 3 else "#ef4444")
        timer_placeholder.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 12px 20px; margin: 8px 0; text-align: center;">
            <div style="color: {timer_color}; font-size: 1.55rem; font-weight: 800; margin-bottom: 4px;">
                ⏳ Time Remaining: {remaining}s / 15s
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem;">
                Speak continuously and explain your technical reasoning clearly.
            </div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.04)

    # =========================================================================
    # STAGE 5: AUTOMATIC RECORDING STOP & PROCESSING
    # =========================================================================
    if camera is not None:
        camera.release()
    camera_placeholder.empty()
    timer_placeholder.empty()

    stage_status_placeholder.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px; margin: 10px 0; text-align: center;">
        <span style="color: #38bdf8; font-size: 1.1rem; font-weight: 700;">
            🧠 Processing Question {curr_q_num} answer and visual analysis...
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Processing Question {curr_q_num} response..."):
        audio_thread.join(timeout=8.0)
        transcribed_text = audio_result[0] if audio_result else ""

        input_key = f"tech_ans_input_{curr_idx}"
        prev_ans = st.session_state.get(input_key, "").strip()

        if transcribed_text.startswith("ERROR:"):
            st.session_state.last_audio_error = transcribed_text
            # Never erase candidate's existing answer on transcription error!
            if prev_ans:
                save_current_technical_answer(curr_idx, method="text", audio_path=audio_path)
            else:
                save_current_technical_answer(curr_idx, method="voice", audio_path=audio_path)
        else:
            st.session_state.last_audio_error = None
            transcribed_clean = transcribed_text.strip()
            st.session_state.technical_transcripts[curr_idx] = transcribed_clean
            st.session_state.technical_raw_transcripts[curr_idx] = transcribed_clean
            st.session_state[input_key] = transcribed_clean

            # Audio fluency and behavioral quality analysis
            a_res = analyze_audio_behavior(transcribed_clean, 15)
            st.session_state.technical_audio_results[curr_idx] = a_res

            save_current_technical_answer(
                curr_idx,
                method="voice",
                raw_transcript=transcribed_clean,
                audio_path=audio_path
            )

        # MediaPipe visual, head-pose, eye-gaze and posture analysis
        st.session_state.technical_frames[curr_idx] = sampled_frames
        v_res = analyze_technical_question_frames(
            sampled_frames,
            question_id=curr_idx + 1,
            domain=q_domain,
            skill=q_skill
        )
        st.session_state.technical_video_results[curr_idx] = v_res

    # =========================================================================
    # STAGE 6: AUTOMATIC NEXT QUESTION TRANSITION
    # =========================================================================
    if curr_idx + 1 < total_q:
        stage_status_placeholder.markdown(f"""
        <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 12px; padding: 16px; margin: 10px 0; text-align: center;">
            <span style="color: #4ade80; font-size: 1.1rem; font-weight: 700;">
                ✅ Question {curr_q_num} recorded! Moving to Question {curr_q_num + 1}...
            </span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1.2)
        st.session_state.technical_question_index += 1
        st.session_state.technical_interview_stage = "QUESTION_DISPLAY"
        scroll_to_top()
        st.rerun()
    else:
        stage_status_placeholder.markdown("""
        <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 12px; padding: 16px; margin: 10px 0; text-align: center;">
            <span style="color: #4ade80; font-size: 1.15rem; font-weight: 700;">
                🎉 All technical questions completed! Proceeding to submission summary...
            </span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1.5)
        st.session_state.technical_interview_completed = True
        st.session_state.technical_interview_submitted = True
        st.session_state.current_page = 'technical_submission'
        scroll_to_top()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
