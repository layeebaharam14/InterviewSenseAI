import streamlit as st
import os
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


def render_technical_submission_page():
    """Renders the Step 4 Technical Interview Submission Summary and Candidate Answer Review Page."""
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
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
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 16px; padding: 20px 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45); max-width: 820px; margin: 0.8rem auto 1.2rem auto; text-align: left;">
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

    # Detailed Question and Answer Breakdown Accordion with Voice Playback & Editing
    st.subheader("🔍 Review & Refine Submitted Answers")
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem;'>Review each question, listen to your audio recording, refine your answers, or re-transcribe speech before final technical evaluation.</p>", unsafe_allow_html=True)

    for i, q_data in enumerate(st.session_state.technical_questions):
        ans_entry = st.session_state.technical_answers.get(i, {})
        ans_text = ans_entry.get("answer_text", "").strip()
        ans_method = ans_entry.get("answer_method", "text")
        audio_file = st.session_state.technical_audio_files.get(i) or ans_entry.get("audio_path")
        has_audio = audio_file and os.path.exists(audio_file)
        is_answered = bool(ans_text)
        status_label = "✅ Answered" if is_answered else "⚠️ Unanswered"
        
        q_title = f"{status_label} — Q{i+1}: {q_data.get('question')}"
        with st.expander(q_title, expanded=(i == 0)):
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <span class="meta-tag meta-tag-skill">{q_data.get('skill', 'General')}</span>
                <span class="meta-tag meta-tag-diff">{q_data.get('difficulty', st.session_state.technical_difficulty)}</span>
                <span class="meta-tag meta-tag-type">{q_data.get('question_type', 'Conceptual')}</span>
                <span class="meta-tag" style="background: rgba(56, 189, 248, 0.12); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3);">👁️ Visuals: {st.session_state.technical_video_results.get(i, {}).get('face_visibility_pct', 0.0)}% visibility</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Question:** {q_data.get('question')}")
            st.write("---")

            # Audio Recovery & Playback Controls
            if has_audio:
                col_aud1, col_aud2 = st.columns([2.5, 1.5])
                with col_aud1:
                    st.caption("🎙️ Recorded Voice Audio (15 Seconds):")
                    st.audio(audio_file, format="audio/wav")
                with col_aud2:
                    st.caption("Audio Recovery:")
                    if st.button("🔄 Re-transcribe Audio", key=f"btn_retranscribe_{i}", type="secondary", use_container_width=True):
                        with st.spinner("Re-transcribing audio recording..."):
                            success, result_text = transcribe_audio_file(
                                audio_file,
                                domain=q_data.get("domain", st.session_state.technical_domain),
                                skills=[q_data.get("skill", "General")]
                            )
                            if success:
                                st.session_state[f"sub_edit_ans_{i}"] = result_text
                                st.session_state[f"tech_ans_input_{i}"] = result_text
                                ans_entry["answer_text"] = result_text
                                ans_entry["answer_method"] = "voice_retranscribed"
                                st.session_state.technical_answers[i] = ans_entry
                                st.session_state.technical_audio_results[i] = analyze_audio_behavior(result_text, 15)
                                st.success("✅ Re-transcription successful! Answer updated.")
                                st.rerun()
                            else:
                                st.error(f"Re-transcription note: {result_text}")

            # Editable Response Text Area
            edit_key = f"sub_edit_ans_{i}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = ans_text

            edited_val = st.text_area(
                f"Your Answer for Q{i+1} (Editable):",
                value=st.session_state[edit_key],
                height=110,
                key=f"text_area_q_{i}",
                placeholder="Type or edit your technical answer here..."
            )

            # Detect manual edits and update button
            col_save, _ = st.columns([1.5, 3])
            with col_save:
                if st.button(f"💾 Save Q{i+1} Answer", key=f"btn_save_edit_{i}", type="secondary"):
                    clean_edited = edited_val.strip()
                    st.session_state[edit_key] = clean_edited
                    st.session_state[f"tech_ans_input_{i}"] = clean_edited
                    ans_entry["answer_text"] = clean_edited
                    ans_entry["answer_method"] = "edited"
                    st.session_state.technical_answers[i] = ans_entry
                    if clean_edited:
                        st.session_state.technical_audio_results[i] = analyze_audio_behavior(clean_edited, 15)
                    st.success(f"Saved Q{i+1} response!")
                    st.rerun()

            # Live synchronization so unclicked changes before submit are also caught
            if edited_val.strip() != ans_text:
                clean_edited = edited_val.strip()
                ans_entry["answer_text"] = clean_edited
                ans_entry["answer_method"] = "edited"
                st.session_state.technical_answers[i] = ans_entry
                st.session_state[f"tech_ans_input_{i}"] = clean_edited
                if clean_edited:
                    st.session_state.technical_audio_results[i] = analyze_audio_behavior(clean_edited, 15)

    st.write("---")

    # Primary Action: Continue to Analysis (Step 5)
    col_a1, col_a2, col_a3 = st.columns([1.5, 1.2, 1])
    with col_a1:
        if st.button("Continue to Analysis →", key="btn_goto_analysis", type="primary", use_container_width=True):
            st.session_state.current_page = 'technical_results'
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

