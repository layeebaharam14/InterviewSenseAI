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

    # Scoped styling for results dashboard components (expanders & actions)
    st.markdown("""
    <style>
    /* Question Expanders: Dark Navy/Blue header with persistent White text across all states */
    .st-key-questions_accordion_group details[data-testid="stExpander"],
    #question-accordions-group + div details[data-testid="stExpander"] {
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 12px !important;
        background: rgba(11, 17, 32, 0.85) !important;
        overflow: hidden !important;
        margin-bottom: 0.65rem !important;
    }

    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary,
    #question-accordions-group + div details[data-testid="stExpander"] > summary {
        background: #0f172a !important; /* Dark navy / blue */
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
    }

    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:hover,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:focus,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:active,
    .st-key-questions_accordion_group details[data-testid="stExpander"][open] > summary {
        background: #1e293b !important;
        color: #ffffff !important;
    }

    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary p,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary span,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary div,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:hover p,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:hover span,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary:hover div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary svg,
    .st-key-questions_accordion_group details[data-testid="stExpander"] > summary [data-testid="stExpanderToggleIcon"] {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* Disclaimer Expander: White header with persistent Black/Dark text across all states */
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"],
    #disclaimers-accordion-group + div details[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        background: rgba(11, 17, 32, 0.85) !important;
        overflow: hidden !important;
    }

    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary,
    #disclaimers-accordion-group + div details[data-testid="stExpander"] > summary {
        background: #ffffff !important; /* White background */
        color: #0f172a !important; /* Dark text */
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
    }

    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:hover,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:focus,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:active,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"][open] > summary {
        background: #f1f5f9 !important; /* Subtle off-white */
        color: #0f172a !important;
    }

    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary p,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary span,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary div,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:hover p,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:hover span,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary:hover div {
        color: #0f172a !important; /* Black/Dark text */
        font-weight: 700 !important;
    }

    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary svg,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] > summary [data-testid="stExpanderToggleIcon"] {
        fill: #0f172a !important;
        color: #0f172a !important;
    }

    /* Disclaimer Expanded Details Interior: Dark background and readable white/slate text */
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background: rgba(11, 17, 32, 0.95) !important;
        padding: 1.2rem !important;
    }

    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] li,
    .st-key-disclaimers_accordion_group details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] strong {
        color: #e2e8f0 !important;
    }

    /* Action Buttons: Exact 1:1 visual match between PDF Download and Restart Interview */
    .stDownloadButton, .stDownloadButton > button {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.4rem !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: none !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 0.85rem 1.8rem !important;
        font-size: 1.15rem !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.45) !important;
        max-width: 340px !important;
        display: block !important;
        margin: 0 auto !important;
    }

    .stDownloadButton > button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        filter: brightness(1.15) !important;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.7) !important;
        color: #ffffff !important;
    }

    .stDownloadButton > button:active {
        transform: scale(0.98) translateY(0) !important;
        box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Title and Centered Subtitle
    st.title("📊 Final Interview Verdict")
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-top: -0.5rem; margin-bottom: 1.5rem;'>Comprehensive behavioral and speech evaluation based on your simulation performance.</p>", unsafe_allow_html=True)
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
        st.markdown(
            f"""
            <div data-testid="stMetric" style="display: flex; flex-direction: column; justify-content: flex-start; height: 100%; text-align: center;">
                <div data-testid="stMetricLabel" style="text-align: center; font-size: 1.1rem; color: #cbd5e1; font-weight: 500; margin-bottom: 6px;">
                    Evaluation Coverage
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 10px 14px; text-align: left; font-size: 0.95rem; line-height: 1.6;">
                    <div style="color: #38bdf8; font-weight: 700;">• Audio: <span style="color: #ffffff; font-weight: 600;">{audio_q}/{total_q} questions</span></div>
                    <div style="color: #38bdf8; font-weight: 700;">• Video: <span style="color: #ffffff; font-weight: 600;">{video_q}/{total_q} questions</span></div>
                </div>
                <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 4px; text-align: center; line-height: 1.3;">
                    Audio: transcribed speech · Video: verified visual tracking
                </div>
            </div>
            """,
            unsafe_allow_html=True,
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

    st.markdown('<div id="question-accordions-group"></div>', unsafe_allow_html=True)
    with st.container(key="questions_accordion_group"):
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

                with st.expander(f"{status_icon} Question {q_num}: {q_title}", expanded=False):
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
    st.markdown('<div id="disclaimers-accordion-group"></div>', unsafe_allow_html=True)
    with st.container(key="disclaimers_accordion_group"):
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
            type="primary",
            use_container_width=True,
        )
    with col_act2:
        if st.button("Restart Interview", type="primary", use_container_width=True):
            st.session_state.current_page = "mode_selection"
            st.session_state.question_index = 0
            st.session_state.current_questions = []
            st.session_state.video_results = []
            st.session_state.audio_results = []
            st.session_state.frames = []
            st.session_state.is_recording = False
            st.session_state.analysis_done = False
            st.session_state.question_spoken = False
            st.session_state.hardware_verified = False
            st.session_state.last_audio_error = None
            st.session_state.pop("evaluation_summary", None)
            st.session_state.pop("mock_interview_summary", None)
            scroll_to_top()
            st.rerun()
