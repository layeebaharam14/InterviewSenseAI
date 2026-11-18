"""
hr_results.py — InterviewSense AI
Mock HR Interview Results Page & Performance Dashboard.
Presents structured, professional behavioral and speech feedback with question-by-question analytics
and multi-page PDF export.
"""

import streamlit as st
import re
from datetime import datetime

from src.interviewsense.utils.styling import scroll_to_top
from src.interviewsense.core.scoring import calculate_scores
from src.interviewsense.core.insights import (
    generate_feedback,
    evaluate_mock_question,
    generate_mock_interview_summary,
)
from src.interviewsense.reports.hr_report_pdf import generate_hr_pdf_report


def render_results_page():
    """Renders the Mock HR Interview Results Dashboard with structured analytics and PDF report export."""
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    scroll_to_top()

    st.title("📊 Final Interview Verdict")
    st.write("Comprehensive behavioral and speech evaluation based on your simulation performance.")
    st.write("---")

    # Retrieve session data
    questions = st.session_state.get("current_questions", [])
    v_results = st.session_state.get("video_results", [])
    a_results = st.session_state.get("audio_results", [])
    cand_name = st.session_state.get("candidate_name", "Candidate")

    # Calculate scores and feedback using existing core modules
    scores = calculate_scores(v_results, a_results)
    feedback = generate_feedback(scores)

    # Assemble comprehensive evaluation summary (shared with PDF generator)
    summary = generate_mock_interview_summary(
        questions=questions,
        video_results=v_results,
        audio_results=a_results,
        scores=scores,
        feedback=feedback,
        candidate_name=cand_name,
    )

    total_q = summary["total_questions"]
    audio_q = summary["audio_questions_evaluated"]
    video_q = summary["video_questions_evaluated"]
    overall_score = summary["overall_score"]
    verdict = summary["verdict"]
    score_note = summary["score_note"]
    coverage_status = summary["coverage_status"]

    # -----------------------------------------------------------------
    # A. Overall Performance & Data Notice
    # -----------------------------------------------------------------
    if total_q > 0 and audio_q < total_q:
        unavail = total_q - audio_q
        st.warning(
            f"⚠️ **Audio Notice:** {unavail} of {total_q} question(s) could not be transcribed "
            f"(microphone or recognition issue). Communication was evaluated from {audio_q} answer(s) only. "
            f"Confidence and observable nervousness are still assessed from camera data."
        )

    # Hero score and verdict row
    col_hero1, col_hero2 = st.columns([1.2, 2.8])
    with col_hero1:
        st.metric("Overall Score", f"{overall_score}/100")
    with col_hero2:
        icon = "✅" if "Ready" in verdict and "Not" not in verdict else ("⚠️" if "Improvement" in verdict else "❌")
        st.markdown(
            f"### Final Verdict: <span class='{summary['verdict_class']}'>{verdict} {icon}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Session Coverage:** {coverage_status} ({total_q} Questions Completed)")
        if score_note:
            st.caption(f"ℹ️ {score_note}")

    st.write("---")

    # -----------------------------------------------------------------
    # B. Performance Metrics Breakdown
    # -----------------------------------------------------------------
    st.subheader("📈 Performance Metrics Breakdown")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        conf_display = f"{summary['confidence_score']}/100" if (video_q > 0 or total_q == 0) else "N/A"
        st.metric(
            "Confidence Score",
            conf_display,
            help="Derived from camera engagement, eye gaze direction, and physical presence."
        )
    with col2:
        st.metric(
            "Nervousness Index",
            f"{summary['nervousness_score']}/100",
            help="Estimated from observable physical movement and speech pauses."
        )
    with col3:
        comm_display = (
            f"{summary['communication_score']}/100"
            if summary["communication_score"] is not None
            else "N/A (no audio)"
        )
        st.metric(
            "Communication Score",
            comm_display,
            help="Derived from speaking rate (WPM), speech fluency, and filler word usage."
        )
    with col4:
        st.metric(
            "Evaluation Coverage",
            f"{audio_q}/{total_q} Audio · {video_q}/{total_q} Video",
            help="Proportion of interview questions with complete sensor evaluation."
        )

    st.write("---")

    # -----------------------------------------------------------------
    # C. Executive Feedback: Strengths & Areas to Improve
    # -----------------------------------------------------------------
    st.subheader("💡 Detailed Feedback")
    colA, colB, colC = st.columns(3)

    with colA:
        st.success("**Strengths**")
        for item in summary["strengths"]:
            st.write(f"- {item}")

    with colB:
        st.warning("**Areas to Improve**")
        for item in summary["improvements"]:
            st.write(f"- {item}")

    with colC:
        st.error("**Critical Issues**")
        if summary["critical_issues"]:
            for item in summary["critical_issues"]:
                st.write(f"- {item}")
        else:
            st.write("- None detected. Great composure throughout!")

    st.write("---")

    # -----------------------------------------------------------------
    # D. Question-by-Question Evaluation
    # -----------------------------------------------------------------
    st.subheader("📝 Question-by-Question Evaluation")
    st.write("Detailed breakdown of your spoken responses, audio metrics, and visual body language for every prompt.")

    q_evals = summary.get("question_evaluations", [])

    if q_evals:
        for idx, q_data in enumerate(q_evals):
            q_num = idx + 1
            q_title = q_data.get("question", f"Question {q_num}")
            a_status = q_data.get("audio_status", "unavailable")
            v_status = q_data.get("video_status", "unavailable")
            transcript = q_data.get("transcript", "")

            # Expander header icon
            if a_status == "transcribed" and v_status == "detected":
                status_icon = "✅"
            elif a_status == "transcribed" or v_status == "detected":
                status_icon = "⚠️"
            else:
                status_icon = "❌"

            with st.expander(f"{status_icon} Question {q_num}: {q_title}", expanded=(idx == 0)):
                # Candidate response display
                if a_status == "transcribed":
                    st.markdown(f"**Candidate Response:**\n> \"*{transcript}*\"")
                elif a_status == "silent":
                    st.info("🔇 **Candidate Response:** *No speech was detected during this recording.*")
                else:
                    st.warning("⚠️ **Candidate Response:** *Audio capture was unavailable due to a hardware or recognition error.*")

                # Metrics row
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("**🎙️ Speech & Audio Telemetry:**")
                    if a_status == "transcribed":
                        wpm = q_data.get("words_per_minute", 0.0)
                        words = q_data.get("word_count", 0)
                        rate = q_data.get("speech_rate", "—")
                        fillers = q_data.get("filler_words", 0)
                        pauses = q_data.get("pauses", 0)
                        st.markdown(
                            f"- **Pace:** {wpm} WPM ({rate})\n"
                            f"- **Word Count:** {words} words\n"
                            f"- **Filler Words:** {fillers}\n"
                            f"- **Estimated Pauses:** {pauses}"
                        )
                    elif a_status == "silent":
                        st.markdown("- *Silence recorded (0 words spoken)*")
                    else:
                        st.markdown("- *Audio capture unavailable*")

                with col_m2:
                    st.markdown("**📷 Visual & Composure Telemetry:**")
                    if v_status == "detected":
                        gaze = str(q_data.get("eye_contact", "unavailable")).capitalize()
                        mov = str(q_data.get("movement", "unavailable")).capitalize()
                        pos = str(q_data.get("face_position", "unavailable")).capitalize()
                        posture = str(q_data.get("posture", "unavailable")).capitalize()
                        st.markdown(
                            f"- **Eye Contact:** {gaze}\n"
                            f"- **Composure / Movement:** {mov}\n"
                            f"- **Framing:** {pos}\n"
                            f"- **Posture:** {posture}"
                        )
                    else:
                        st.markdown("- *Face was not clearly detected in frame*")

                # Evidence-based observations
                st.markdown("---")
                col_fb1, col_fb2 = st.columns(2)
                with col_fb1:
                    st.markdown("##### 🌟 What went well")
                    for w in q_data.get("what_went_well", []):
                        st.markdown(f"- {w}")
                with col_fb2:
                    st.markdown("##### 🎯 What to improve")
                    for imp in q_data.get("what_to_improve", []):
                        st.markdown(f"- {imp}")
    else:
        st.info("No question responses were recorded during this session.")

    st.write("---")

    # -----------------------------------------------------------------
    # E. Evaluation Coverage & Scientific Limitations
    # -----------------------------------------------------------------
    with st.expander("ℹ️ Evaluation Limitations & Methodology Disclaimers", expanded=False):
        st.markdown(
            "**Data Coverage & Quality Disclosures:**\n"
            f"- **Questions recorded:** {total_q}\n"
            f"- **Face presence verified:** {video_q}/{total_q} questions\n"
            f"- **Speech transcribed:** {audio_q}/{total_q} questions\n\n"
            "**Scientific & Behavioral Limitations:**\n"
            "- **Observable signals only:** Measurements reflect webcam framing, eye gaze approximations, and speech rate. "
            "They do not measure personality, intelligence, or internal emotional state.\n"
            "- **Non-hallucinatory evaluation:** All metrics are calculated directly from physical sensors and speech transcripts.\n"
            "- **Practice purpose:** This feedback is designed to build confidence and refine delivery for real-world interviews."
        )

    st.write("---")

    # -----------------------------------------------------------------
    # F. Downloadable PDF Report & Navigation
    # -----------------------------------------------------------------
    pdf_bytes = generate_hr_pdf_report(summary)
    clean_date = datetime.now().strftime("%Y%m%d_%H%M")
    pdf_filename = f"InterviewSense_Mock_Report_{clean_date}.pdf"

    col_act1, col_act2 = st.columns([1, 1])
    with col_act1:
        st.download_button(
            label="📄 Download Mock Interview Report (PDF)",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
        )
    with col_act2:
        if st.button("Restart Interview", type="primary", use_container_width=True):
            st.session_state.current_page = "landing"
            st.session_state.current_tab = "Home"
            scroll_to_top()
            st.rerun()
