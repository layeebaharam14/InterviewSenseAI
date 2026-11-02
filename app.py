"""
InterviewSense AI - Main Application Entry Point
Run with:  streamlit run app.py
"""
import streamlit as st

from src.interviewsense.utils.styling import apply_css, scroll_to_top
from src.interviewsense.core.session_state import init_session_state

from src.interviewsense.ui.landing import render_landing_page
from src.interviewsense.ui.mode_selection import render_mode_selection_page
from src.interviewsense.ui.technical_setup import render_technical_setup_page
from src.interviewsense.ui.technical_interview import render_technical_interview_page
from src.interviewsense.ui.technical_submission import render_technical_submission_page
from src.interviewsense.ui.technical_results import render_technical_results_page
from src.interviewsense.ui.hr_interview import render_interview_page
from src.interviewsense.ui.hr_results import render_results_page

# Application Configuration
st.set_page_config(page_title="InterviewSense AI", layout="centered")



# Core Helpers Re-export for Backward Compatibility
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
render_technical_analysis_page = render_technical_results_page

__all__ = [
    "main",
    "init_session_state",
    "QUESTION_POOL",
    "TECHNICAL_DOMAIN_SKILLS",
    "get_question_duration",
    "get_technical_question_duration",
    "get_camera",
    "record_and_transcribe",
    "record_technical_voice_answer",
    "save_current_technical_answer",
    "render_technical_analysis_page",
]


def main():
    apply_css()
    init_session_state()

    # Scroll-to-top anchor
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)

    # Fire scroll-to-top on any meaningful navigation change
    nav_key = (
        st.session_state.get('current_page'),
        st.session_state.get('current_tab'),
        st.session_state.get('technical_interview_stage'),
        st.session_state.get('technical_question_index', 0),
        st.session_state.get('question_index', 0),
        st.session_state.get('technical_hardware_verified', False),
    )
    if st.session_state.get('_last_nav_position') != nav_key:
        st.session_state['_last_nav_position'] = nav_key
        scroll_to_top()

    # Router
    page = st.session_state.current_page

    if page == 'landing':
        render_landing_page()
    elif page == 'mode_selection':
        render_mode_selection_page()
    elif page == 'technical_setup':
        render_technical_setup_page()
    elif page == 'technical_interview':
        render_technical_interview_page()
    elif page in ('technical_submission', 'technical_completed'):
        render_technical_submission_page()
    elif page in ('technical_results', 'technical_analysis', 'technical_analysis_placeholder'):
        render_technical_results_page()
    elif page == 'interview':
        render_interview_page()
    elif page == 'results':
        render_results_page()


if __name__ == "__main__":
    main()
