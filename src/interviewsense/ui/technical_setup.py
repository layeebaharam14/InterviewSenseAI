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
    TECHNICAL_DOMAIN_SKILLS,
    get_question_duration,
    get_technical_question_duration,
    get_camera,
    record_and_transcribe,
    record_technical_voice_answer,
    save_current_technical_answer,
)


def render_technical_setup_page():
    """Renders the Step 2 Technical Interview Domain and Skill Setup Page."""
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    # Navigation buttons
    col_nav1, col_nav2, _ = st.columns([1.3, 1, 3])
    with col_nav1:
        if st.button("← Back to Modes", key="back_to_modes_btn", type="secondary"):
            st.session_state.current_page = 'mode_selection'
            st.rerun()
            return
    with col_nav2:
        if st.button("⌂ Back to Home", key="back_to_home_from_setup", type="secondary"):
            st.session_state.current_page = 'landing'
            st.session_state.current_tab = 'Home'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
    st.title("⚙️ Configure Your Technical Interview")
    st.subheader("Choose your technical domain and skills to generate an interview tailored to your knowledge.")
    st.write("---")

    # Custom styling for setup cards and skill chips
    st.markdown("""
    <style>
    .setup-card {
        background: linear-gradient(145deg, #0b1120, #0f172a);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);
    }
    .setup-step-header {
        color: #38bdf8;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .skill-chip {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #e0f2fe;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    .selected-summary-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px dashed rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    # CANDIDATE PROFILE SECTION
    st.markdown('<div class="setup-card">', unsafe_allow_html=True)
    st.markdown('<div class="setup-step-header">👤 Candidate Profile (Optional)</div>', unsafe_allow_html=True)
    st.caption("Provide your name for personalized report generation and analytics scorecard.")
    cand_input = st.text_input(
        "Candidate Name",
        value=st.session_state.get("candidate_name", ""),
        placeholder="e.g. Alex Johnson",
        key="candidate_name_setup_input",
        label_visibility="collapsed"
    )
    if cand_input != st.session_state.get("candidate_name", ""):
        st.session_state.candidate_name = cand_input.strip()
    st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 1: DOMAIN SELECTION
    st.markdown('<div class="setup-card">', unsafe_allow_html=True)
    st.markdown('<div class="setup-step-header">📌 1. Select Your Technical Domain</div>', unsafe_allow_html=True)
    st.caption("Select the primary programming language or computer science domain for your interview.")

    domain_list = list(TECHNICAL_DOMAIN_SKILLS.keys())
    current_domain_idx = domain_list.index(st.session_state.technical_domain) if st.session_state.technical_domain in domain_list else 0

    selected_domain = st.selectbox(
        "Technical Domain",
        options=domain_list,
        index=current_domain_idx,
        key="tech_domain_select",
        label_visibility="collapsed"
    )

    # Detect domain change and reset skills
    if selected_domain != st.session_state.previous_technical_domain:
        st.session_state.technical_domain = selected_domain
        st.session_state.previous_technical_domain = selected_domain
        st.session_state.technical_skills = []
        for k in list(st.session_state.keys()):
            if k.startswith("skill_chk_"):
                del st.session_state[k]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 2: SKILL SELECTION
    available_skills = TECHNICAL_DOMAIN_SKILLS[st.session_state.technical_domain]

    st.markdown('<div class="setup-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="setup-step-header">🎯 2. Select Your Skills ({st.session_state.technical_domain})</div>', unsafe_allow_html=True)
    st.caption("Select one or more topics. When you switch domains, skill selections automatically reset.")

    # Select All / Clear Selection Controls
    col_s1, col_s2, _ = st.columns([1, 1.2, 2.5])
    with col_s1:
        if st.button("✓ Select All", key="btn_select_all_skills", type="secondary"):
            st.session_state.technical_skills = list(available_skills)
            for s in available_skills:
                st.session_state[f"skill_chk_{st.session_state.technical_domain}_{s}"] = True
            st.rerun()
    with col_s2:
        if st.button("✕ Clear Selection", key="btn_clear_skills", type="secondary"):
            st.session_state.technical_skills = []
            for s in available_skills:
                st.session_state[f"skill_chk_{st.session_state.technical_domain}_{s}"] = False
            st.rerun()

    # Dynamic Checkboxes in 2 Columns
    col_left, col_right = st.columns(2)
    selected_now = []

    for idx, skill in enumerate(available_skills):
        target_col = col_left if (idx % 2 == 0) else col_right
        chk_key = f"skill_chk_{st.session_state.technical_domain}_{skill}"
        if chk_key not in st.session_state:
            st.session_state[chk_key] = (skill in st.session_state.technical_skills)
        
        # Checkbox bound directly to key without redundant value parameter
        checked = target_col.checkbox(
            skill,
            key=chk_key
        )
        if checked:
            selected_now.append(skill)

    # Keep session state updated with user's interactive selections
    st.session_state.technical_skills = selected_now

    # Clear display of selected skills
    if st.session_state.technical_skills:
        chips_markup = "".join([f'<span class="skill-chip">{s}</span>' for s in st.session_state.technical_skills])
        st.markdown(f"""
        <div class="selected-summary-box">
            <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 700; margin-bottom: 6px;">
                ACTIVE TOPICS ({len(st.session_state.technical_skills)} SELECTED):
            </div>
            <div>{chips_markup}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please select at least one skill to enable generating the technical interview.")

    st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 3 & 4: DIFFICULTY AND QUESTION COUNT
    col_d, col_q = st.columns(2, gap="large")

    with col_d:
        st.markdown('<div class="setup-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="setup-step-header">📊 3. Interview Difficulty</div>', unsafe_allow_html=True)
        st.caption("Select the question challenge level.")
        
        difficulty_options = ["Beginner", "Intermediate", "Advanced"]
        diff_idx = difficulty_options.index(st.session_state.technical_difficulty) if st.session_state.technical_difficulty in difficulty_options else 1
        
        selected_diff = st.selectbox(
            "Difficulty Level",
            options=difficulty_options,
            index=diff_idx,
            key="tech_diff_select",
            label_visibility="collapsed"
        )
        st.session_state.technical_difficulty = selected_diff
        st.markdown('</div>', unsafe_allow_html=True)

    with col_q:
        st.markdown('<div class="setup-card" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div class="setup-step-header">🔢 4. Number of Questions</div>', unsafe_allow_html=True)
        st.caption("Select the total question length.")
        
        question_count_options = ["5 Questions", "10 Questions", "15 Questions"]
        count_idx = question_count_options.index(st.session_state.technical_num_questions) if st.session_state.technical_num_questions in question_count_options else 0
        
        selected_count = st.selectbox(
            "Questions Count",
            options=question_count_options,
            index=count_idx,
            key="tech_num_q_select",
            label_visibility="collapsed"
        )
        st.session_state.technical_num_questions = selected_count
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # SECTION 5: GENERATE TECHNICAL INTERVIEW BUTTON WITH VALIDATION & GENERATION ENGINE
    if st.button("🚀 Generate Technical Interview", key="btn_generate_tech_interview", type="primary", use_container_width=True):
        # Validations
        if not st.session_state.technical_domain:
            st.error("Please select a technical domain.")
        elif not st.session_state.technical_skills:
            st.error("⚠️ Please select at least one skill before proceeding to generate the technical interview.")
        elif not st.session_state.technical_difficulty:
            st.error("Please select an interview difficulty.")
        else:
            # Parse requested question count
            try:
                num_q = int(str(st.session_state.technical_num_questions).split()[0])
            except Exception:
                num_q = 5
                
            # Generate technical questions from the question bank
            generated_qs = generate_technical_questions(
                domain=st.session_state.technical_domain,
                skills=st.session_state.technical_skills,
                difficulty=st.session_state.technical_difficulty,
                num_questions=num_q
            )
            
            if not generated_qs:
                st.error("Unable to find questions matching the selected criteria. Please select additional skills.")
            else:
                st.session_state.technical_questions = generated_qs
                st.session_state.technical_question_index = 0
                st.session_state.technical_interview_stage = "QUESTION_DISPLAY"
                st.session_state.technical_answers = {}
                st.session_state.technical_frames = {}
                st.session_state.technical_video_results = {}
                st.session_state.technical_audio_results = {}
                st.session_state.technical_interview_completed = False
                st.session_state.technical_interview_submitted = False
                st.session_state.confirm_end_technical = False
                st.session_state.confirm_submit_technical = False
                st.session_state.technical_evaluation_results = None
                st.session_state.technical_overall_score = 0
                st.session_state.technical_performance_level = "Needs Improvement"
                st.session_state.technical_evaluation_completed = False
                # Clear previous technical answer input and speech session keys
                for k in list(st.session_state.keys()):
                    if any(k.startswith(prefix) for prefix in [
                        "tech_ans_input_", "voice_dur_", "tech_spoken_",
                        "tech_countdown_done_", "sub_edit_ans_", "text_area_q_"
                    ]):
                        del st.session_state[k]
                st.session_state.current_page = 'technical_interview'
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

