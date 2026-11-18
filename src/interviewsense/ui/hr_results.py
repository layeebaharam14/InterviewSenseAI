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
    scroll_to_top()
    st.title("📊 Final Interview Verdict")
    st.write("Here is the analysis of your performance based on behavioural and speech metrics.")
    st.write("---")

    # Calculate final scores
    scores = calculate_scores(st.session_state.video_results, st.session_state.audio_results)

    total_q = len(st.session_state.video_results)
    audio_q = scores.get("audio_questions_evaluated", 0)
    video_q = scores.get("video_questions_evaluated", 0)

    # -----------------------------------------------------------------
    # Data-availability notice — shown when audio was partially missing
    # -----------------------------------------------------------------
    if audio_q < total_q and total_q > 0:
        unavail = total_q - audio_q
        st.warning(
            f"⚠️ **Audio note:** {unavail} of {total_q} question(s) could not be transcribed "
            f"(microphone or network issue). Communication was evaluated from {audio_q} answer(s) only. "
            f"Confidence and observable nervousness are still assessed from camera data."
        )

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence Score", f"{scores['confidence']}/100")
    with col2:
        st.metric("Nervousness Index", f"{scores['nervousness']}/100")
    with col3:
        comm_label = (
            f"{scores['communication']}/100"
            if audio_q > 0
            else "N/A (no audio)"
        )
        st.metric("Communication Score", comm_label)

    # Supplementary camera / audio coverage info
    if total_q > 0:
        with st.expander("📋 Evaluation Coverage Details", expanded=False):
            st.markdown(
                f"- **Questions recorded:** {total_q}\n"
                f"- **Questions with face detected (camera evidence):** {video_q}/{total_q}\n"
                f"- **Questions with transcribed audio:** {audio_q}/{total_q}"
            )
            if audio_q == 0:
                st.info(
                    "No audio was transcribed during this session. "
                    "The Communication score is excluded from the overall verdict. "
                    "Please check your microphone settings and try again."
                )

    st.write("---")

    # Generate Feedback
    feedback = generate_feedback(scores)

    # score_note (e.g. if communication was excluded from average)
    score_note = feedback.get("score_note", "")

    # Display Verdict
    icon = "✅" if "Ready" in feedback["verdict"] else ("⚠️" if "Improvement" in feedback["verdict"] else "❌")
    st.markdown(
        f"### Final Verdict: <span class='{feedback['verdict_class']}'>{feedback['verdict']} {icon}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"**Overall Score:** {feedback['overall_score']}/100")
    if score_note:
        st.caption(f"ℹ️ {score_note}")

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
        if feedback["negative"]:
            for item in feedback["negative"]:
                st.write(f"- {item}")
        else:
            st.write("- None detected. Great job!")

    # -----------------------------------------------------------------
    # Per-question audio summary (collapsed by default)
    # -----------------------------------------------------------------
    if st.session_state.audio_results:
        st.write("---")
        with st.expander("🎙️ Per-Question Audio Summary", expanded=False):
            questions = st.session_state.get("current_questions", [])
            for i, a_res in enumerate(st.session_state.audio_results):
                q_label = f"Q{i + 1}"
                if i < len(questions):
                    q_label += f": {questions[i][:60]}{'…' if len(questions[i]) > 60 else ''}"
                avail = a_res.get("audio_available", True)
                if not avail:
                    st.markdown(f"**{q_label}** — ⚠️ Audio unavailable (transcription failed)")
                elif not a_res.get("meaningful", True):
                    st.markdown(f"**{q_label}** — 🔇 No speech detected (silence)")
                else:
                    wpm = a_res.get("words_per_minute", 0)
                    words = a_res.get("word_count", 0)
                    rate = a_res.get("speech_rate", "—")
                    fillers = a_res.get("filler_words", 0)
                    transcript = a_res.get("transcribed_text", "")
                    st.markdown(
                        f"**{q_label}** — ✅ {words} words · {wpm} WPM · {rate} pace"
                        + (f" · {fillers} filler word(s)" if fillers else "")
                    )
                    if transcript:
                        st.caption(f'📝 "{transcript[:200]}{"…" if len(transcript) > 200 else ""}"')

    st.write("---")
    if st.button("Restart Interview", type="primary", use_container_width=True):
        st.session_state.current_page = "landing"
        st.session_state.current_tab = "Home"
        scroll_to_top()
        st.rerun()
