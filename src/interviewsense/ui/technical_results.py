import streamlit as st
import streamlit.components.v1 as components
import cv2
import time
import threading
import speech_recognition as sr
import re
import uuid
from datetime import datetime

import html
from src.interviewsense.utils.styling import scroll_to_top, apply_css, speak_question, render_html, clean_html
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


def render_technical_results_page():
    """Renders the Step 6 Final Technical Interview Results Dashboard (Phase 4 Full Analytics)."""
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    if not st.session_state.get("technical_questions"):
        st.session_state.current_page = 'technical_setup'
        st.rerun()
        return

    # Trigger evaluation once if not yet completed for this session
    if not st.session_state.get("technical_evaluation_completed") or st.session_state.get("technical_evaluation_results") is None:
        with st.spinner("🧠 Evaluating your technical responses across accuracy, depth, relevance, and completeness..."):
            time.sleep(0.8) # UX transition indicator
            results = evaluate_technical_interview(
                st.session_state.technical_questions,
                st.session_state.technical_answers
            )
            st.session_state.technical_evaluation_results = results
            st.session_state.technical_overall_score = results["overall_score"]
            st.session_state.technical_performance_level = results["performance_level"]
            st.session_state.technical_evaluation_completed = True
            st.rerun()
            return

    results = st.session_state.technical_evaluation_results
    overall_sc = results.get("overall_score", 0)
    perf_level = results.get("performance_level", "Good")

    # Styling for performance classification badge and theme
    if perf_level == "Excellent":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#4ade80", "rgba(34, 197, 94, 0.15)", "rgba(34, 197, 94, 0.4)", "🌟"
    elif perf_level == "Very Good":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#38bdf8", "rgba(56, 189, 248, 0.15)", "rgba(56, 189, 248, 0.4)", "✅"
    elif perf_level == "Good":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#facc15", "rgba(250, 204, 21, 0.15)", "rgba(250, 204, 21, 0.4)", "👍"
    elif perf_level == "Needs Improvement":
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#fb923c", "rgba(251, 146, 60, 0.15)", "rgba(251, 146, 60, 0.4)", "⚠️"
    else:
        lvl_color, lvl_bg, lvl_border, lvl_icon = "#f87171", "rgba(239, 68, 68, 0.15)", "rgba(239, 68, 68, 0.4)", "❌"

    # Audio and Visual Telemetry
    audio_results = st.session_state.get("technical_audio_results", {})
    overall_vis = calculate_overall_visual_analysis(st.session_state.get("technical_video_results", {}))
    st.session_state.technical_overall_visual_analysis = overall_vis

    # Generate Combined Synthesis and Personalised Roadmap
    combined_summary = generate_combined_summary(results, audio_results, overall_vis)
    roadmap = generate_improvement_roadmap(results, audio_results, overall_vis)

    candidate_name = st.session_state.get("candidate_name") or "Candidate"
    interview_timestamp = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    # Top Sub-Navigation
    col_t1, col_t2 = st.columns([1.5, 3.5])
    with col_t1:
        if st.button("← Submission Summary", key="btn_back_to_sub_top", type="secondary"):
            st.session_state.current_page = 'technical_submission'
            st.rerun()
            return

    st.markdown('<div class="page-section" style="padding-top: 0.2rem;">', unsafe_allow_html=True)
    
    # Mode Badge
    st.markdown('<div style="text-align:center;"><div class="mode-badge" style="background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.4); color: #7dd3fc;">⚡ Technical Interview Results Dashboard</div></div>', unsafe_allow_html=True)
    
    # Heading and Subtitle
    st.title("Your Technical Interview Results")
    st.markdown(f"<p style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 1.5rem;'>Comprehensive performance evaluation and analytics for <strong>{candidate_name}</strong>.</p>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION A: INTERVIEW OVERVIEW & OVERALL SCORECARDS
    # -------------------------------------------------------------------------
    skills_chips_html = "".join([f'<span class="skill-chip">{s}</span>' for s in st.session_state.technical_skills])
    render_html(f"""
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 16px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 12px;">
            <div>
                <span style="color: #38bdf8; font-weight: 700; font-size: 1.1rem;">📋 Interview Overview</span>
                <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 10px;">• {interview_timestamp}</span>
            </div>
            <div>
                <span style="display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; color: #4ade80; background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.35);">
                    Status: Completed
                </span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; font-size: 0.9rem;">
            <div><strong style="color: #94a3b8;">Candidate:</strong> <span style="color: #ffffff; font-weight: 600;">{candidate_name}</span></div>
            <div><strong style="color: #94a3b8;">Primary Domain:</strong> <span style="color: #ffffff;">{st.session_state.technical_domain}</span></div>
            <div><strong style="color: #94a3b8;">Difficulty Tier:</strong> <span style="color: #ffffff;">{st.session_state.technical_difficulty}</span></div>
            <div><strong style="color: #94a3b8;">Total Questions:</strong> <span style="color: #ffffff;">{results['total_questions']} Questions</span></div>
            <div><strong style="color: #94a3b8;">Completed:</strong> <span style="color: #4ade80; font-weight: 600;">{results['answered_questions']} Answered</span></div>
            <div><strong style="color: #94a3b8;">Skipped / Blank:</strong> <span style="color: #fb923c; font-weight: 600;">{results['unanswered_questions']} Unanswered</span></div>
        </div>
        <div style="margin-top: 12px; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 10px;">
            <strong style="color: #94a3b8; font-size: 0.85rem;">Skills Assessed:</strong>
            <div style="margin-top: 4px;">{skills_chips_html if skills_chips_html else '<span style="color:#cbd5e1;">General Technical Domain</span>'}</div>
        </div>
    </div>
    """)

    # Circular Score Radial Visualization
    dash_circumference = 314 # 2 * pi * r (r=50)
    dash_offset = dash_circumference - (dash_circumference * (overall_sc / 100.0))

    render_html(f"""
    <div style="background: linear-gradient(145deg, #0b1120, #0f172a); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 20px; padding: 22px 24px; box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5); max-width: 860px; margin: 0.5rem auto 1.5rem auto;">
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-around; gap: 20px;">
            <!-- Circular Score Gauge -->
            <div style="text-align: center;">
                <svg width="150" height="150" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10"/>
                    <circle cx="60" cy="60" r="50" fill="none" stroke="{lvl_color}" stroke-width="10"
                            stroke-linecap="round"
                            stroke-dasharray="{dash_circumference}"
                            stroke-dashoffset="{dash_offset}"
                            transform="rotate(-90 60 60)"
                            style="filter: drop-shadow(0 0 8px {lvl_color}); transition: stroke-dashoffset 1s ease-in-out;"/>
                    <text x="60" y="58" font-size="28" font-weight="900" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">{overall_sc}</text>
                    <text x="60" y="78" font-size="11" font-weight="600" fill="#94a3b8" text-anchor="middle">OUT OF 100</text>
                </svg>
                <div style="margin-top: 8px;">
                    <span style="display: inline-block; padding: 5px 16px; border-radius: 20px; font-weight: 700; font-size: 0.95rem; color: {lvl_color}; background: {lvl_bg}; border: 1px solid {lvl_border};">
                        {lvl_icon} {perf_level}
                    </span>
                </div>
            </div>

            <!-- Score Cards Grid -->
            <div style="flex: 1; min-width: 300px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; text-align: left;">
                    <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Total Questions</div>
                    <div style="color: #ffffff; font-size: 1.6rem; font-weight: 800; margin-top: 2px;">{results['total_questions']}</div>
                </div>
                <div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 12px; padding: 14px 18px; text-align: left;">
                    <div style="color: #4ade80; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Answered Questions</div>
                    <div style="color: #4ade80; font-size: 1.6rem; font-weight: 800; margin-top: 2px;">{results['answered_questions']}</div>
                </div>
                <div style="background: rgba(251, 146, 60, 0.08); border: 1px solid rgba(251, 146, 60, 0.25); border-radius: 12px; padding: 14px 18px; text-align: left;">
                    <div style="color: #fb923c; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Unanswered (Zero Marks)</div>
                    <div style="color: #fb923c; font-size: 1.6rem; font-weight: 800; margin-top: 2px;">{results['unanswered_questions']}</div>
                </div>
                <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 14px 18px; text-align: left;">
                    <div style="color: #38bdf8; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Average Question Score</div>
                    <div style="color: #38bdf8; font-size: 1.6rem; font-weight: 800; margin-top: 2px;">{results['average_score']}<span style="font-size: 1rem; color: #94a3b8;">/100</span></div>
                </div>
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------------------
    # TABBED ANALYTICS DASHBOARD
    # -------------------------------------------------------------------------
    tab_summary, tab_tech, tab_audio, tab_vis, tab_questions = st.tabs([
        "🏆 Combined Summary & Roadmap",
        "💻 Technical Performance",
        "🎙️ Speech & Communication",
        "👁️ Facial & Visual Behaviour",
        "🔍 Question-Wise Detailed Analysis"
    ])

    evals = results.get("evaluations", [])
    tot_evals = max(len(evals), 1)
    avg_correctness = round(sum(e.get("criteria_scores", {}).get("technical_correctness", 0) for e in evals) / tot_evals, 1)
    avg_concepts = round(sum(e.get("criteria_scores", {}).get("conceptual_understanding", 0) for e in evals) / tot_evals, 1)
    avg_relevance = round(sum(e.get("criteria_scores", {}).get("relevance", 0) for e in evals) / tot_evals, 1)
    avg_completeness = round(sum(e.get("criteria_scores", {}).get("completeness", 0) for e in evals) / tot_evals, 1)
    avg_quality = round(sum(e.get("criteria_scores", {}).get("explanation_quality", 0) for e in evals) / tot_evals, 1)

    # -------------------------------------------------------------------------
    # TAB 1: COMBINED PERFORMANCE SUMMARY & PERSONALISED ROADMAP
    # -------------------------------------------------------------------------
    with tab_summary:
        st.subheader("🎯 Synthesized Performance Summary")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Cross-dimensional analysis across technical correctness, spoken delivery, and visual engagement:</p>", unsafe_allow_html=True)

        col_st1, col_st2 = st.columns(2)
        with col_st1:
            tech_s_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>✅ {s}</div>" for s in combined_summary.get("technical_strengths", [])])
            if not tech_s_items:
                tech_s_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>Focus on practicing core concepts to build key strengths.</div>"
            render_html(f"""
            <div style="background: rgba(34, 197, 94, 0.06); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                <div style="color: #4ade80; font-weight: 700; font-size: 1rem; margin-bottom: 8px;">💪 Technical Strengths</div>
                {tech_s_items}
            </div>
            """)

            comm_s_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>💬 {cs}</div>" for cs in combined_summary.get("communication_strengths", [])])
            if not comm_s_items:
                comm_s_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>Keep speaking clearly and at a steady pace.</div>"
            render_html(f"""
            <div style="background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 18px;">
                <div style="color: #38bdf8; font-weight: 700; font-size: 1rem; margin-bottom: 8px;">🎙️ Communication Strengths</div>
                {comm_s_items}
            </div>
            """)

        with col_st2:
            weak_t_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>🎯 {w}</div>" for w in combined_summary.get("weak_technical_areas", [])])
            if not weak_t_items:
                weak_t_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>No major technical weaknesses detected!</div>"
            render_html(f"""
            <div style="background: rgba(251, 146, 60, 0.06); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                <div style="color: #fb923c; font-weight: 700; font-size: 1rem; margin-bottom: 8px;">⚠️ Weak Technical Areas</div>
                {weak_t_items}
            </div>
            """)

            comm_i_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>💡 {ci}</div>" for ci in combined_summary.get("communication_improvements", [])])
            if not comm_i_items:
                comm_i_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>Communication was clear and fluent throughout.</div>"
            render_html(f"""
            <div style="background: rgba(192, 132, 252, 0.06); border: 1px solid rgba(192, 132, 252, 0.3); border-radius: 12px; padding: 18px;">
                <div style="color: #c084fc; font-weight: 700; font-size: 1rem; margin-bottom: 8px;">🗣️ Communication Focus Areas</div>
                {comm_i_items}
            </div>
            """)

        # Topics to Revise Box
        st.write("---")
        st.subheader("📚 Concrete Topics to Revise")
        topics = combined_summary.get("topics_to_revise", [])
        if topics:
            t_cols = st.columns(min(len(topics), 3))
            for idx, top in enumerate(topics[:6]):
                target_col = t_cols[idx % min(len(topics), 3)]
                with target_col:
                    render_html(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border-left: 3px solid #38bdf8; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px;">
                        <span style="color: #7dd3fc; font-size: 0.88rem; font-weight: 600;">{top}</span>
                    </div>
                    """)

        # Personalised Improvement Roadmap Section
        st.write("---")
        st.subheader("🗺️ Personalised Improvement Roadmap")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Actionable, prioritized recommendations directly linked to your interview results:</p>", unsafe_allow_html=True)

        tier_cols = st.columns(3)
        # High Priority
        with tier_cols[0]:
            high_items = "".join([
                f'''<div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    <div style="color: #ffffff; font-weight: 600; font-size: 0.85rem;">{item.get('title')}</div>
                    <div style="color: #cbd5e1; font-size: 0.8rem; margin: 4px 0;">{item.get('description')}</div>
                    <div style="color: #38bdf8; font-size: 0.78rem; font-weight: 600;">→ Action: {item.get('action')}</div>
                </div>'''
                for item in roadmap.get("high_priority", [])
            ])
            render_html(f"""
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="color: #f87171; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">🔴 HIGH PRIORITY</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 12px;">Immediate concept and skipped topic revision</div>
                {high_items}
            </div>
            """)

        # Medium Priority
        with tier_cols[1]:
            med_items = "".join([
                f'''<div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    <div style="color: #ffffff; font-weight: 600; font-size: 0.85rem;">{item.get('title')}</div>
                    <div style="color: #cbd5e1; font-size: 0.8rem; margin: 4px 0;">{item.get('description')}</div>
                    <div style="color: #38bdf8; font-size: 0.78rem; font-weight: 600;">→ Action: {item.get('action')}</div>
                </div>'''
                for item in roadmap.get("medium_priority", [])
            ])
            render_html(f"""
            <div style="background: rgba(251, 146, 60, 0.08); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="color: #fb923c; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">🟡 MEDIUM PRIORITY</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 12px;">Technical depth, edge cases & pacing calibration</div>
                {med_items}
            </div>
            """)

        # Further Practice
        with tier_cols[2]:
            fp_items = "".join([
                f'''<div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    <div style="color: #ffffff; font-weight: 600; font-size: 0.85rem;">{item.get('title')}</div>
                    <div style="color: #cbd5e1; font-size: 0.8rem; margin: 4px 0;">{item.get('description')}</div>
                    <div style="color: #38bdf8; font-size: 0.78rem; font-weight: 600;">→ Action: {item.get('action')}</div>
                </div>'''
                for item in roadmap.get("further_practice", [])
            ])
            render_html(f"""
            <div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="color: #4ade80; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">🟢 FURTHER PRACTICE</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 12px;">Long-term architectural mastery & simulation</div>
                {fp_items}
            </div>
            """)

    # -------------------------------------------------------------------------
    # TAB 2: TECHNICAL PERFORMANCE BREAKDOWN
    # -------------------------------------------------------------------------
    with tab_tech:
        col_vis1, col_vis2 = st.columns([1.1, 1])

        with col_vis1:
            st.subheader("📊 Evaluation Criteria")
            st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Average performance across all 5 evaluation criteria:</p>", unsafe_allow_html=True)
            
            criteria_list = [
                ("Technical Correctness", avg_correctness, 40, "#38bdf8"),
                ("Conceptual Understanding", avg_concepts, 25, "#c084fc"),
                ("Relevance", avg_relevance, 15, "#4ade80"),
                ("Completeness", avg_completeness, 15, "#fb923c"),
                ("Explanation Quality", avg_quality, 5, "#facc15"),
            ]

            for c_label, c_val, c_max, c_color in criteria_list:
                pct = int((c_val / c_max) * 100) if c_max > 0 else 0
                render_html(f"""
                <div style="margin-bottom: 10px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;">
                        <span style="color: #ffffff;">{c_label}</span>
                        <span style="color: {c_color}; font-weight: 700;">{c_val} / {c_max} ({pct}%)</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.08); border-radius: 4px; height: 6px; overflow: hidden;">
                        <div style="background: {c_color}; width: {pct}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                """)

            # Criteria Chart
            crit_chart_data = {
                "Score %": [int((c_val / c_max) * 100) if c_max > 0 else 0 for _, c_val, c_max, _ in criteria_list]
            }
            try:
                import pandas as pd
                crit_df = pd.DataFrame(crit_chart_data, index=[c_label for c_label, _, _, _ in criteria_list])
                st.bar_chart(crit_df, height=180)
            except Exception:
                pass

        with col_vis2:
            st.subheader("🎯 Skill-wise Performance")
            st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Evaluated mastery by technical sub-skill:</p>", unsafe_allow_html=True)
            
            skill_avgs = results.get("skill_averages", {})
            if skill_avgs:
                for sk_name, sk_score in skill_avgs.items():
                    sk_lvl = classify_performance(sk_score)
                    sk_col = "#4ade80" if sk_score >= 75 else "#facc15" if sk_score >= 60 else "#fb923c" if sk_score >= 40 else "#f87171"
                    render_html(f"""
                    <div style="margin-bottom: 10px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;">
                            <span style="color: #ffffff;">{sk_name}</span>
                            <span style="color: {sk_col}; font-weight: 700;">{sk_score}/100 • {sk_lvl}</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.08); border-radius: 4px; height: 6px; overflow: hidden;">
                            <div style="background: {sk_col}; width: {min(100, int(sk_score))}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    """)
                
                try:
                    import pandas as pd
                    sk_df = pd.DataFrame({"Average Score": list(skill_avgs.values())}, index=list(skill_avgs.keys()))
                    st.bar_chart(sk_df, height=180)
                except Exception:
                    pass
            else:
                st.info("No skill data available.")

        # Difficulty Tier Breakdown
        st.write("---")
        st.subheader("📈 Performance Across Difficulty Tiers & Questions")
        diff_avgs = results.get("difficulty_averages", {})
        if diff_avgs:
            d_cols = st.columns(len(diff_avgs))
            for idx, (df_name, df_sc) in enumerate(diff_avgs.items()):
                with d_cols[idx]:
                    st.metric(f"Tier: {df_name}", f"{df_sc} / 100", delta=classify_performance(df_sc))

        # Question-by-Question Score Bar Chart
        if evals:
            try:
                import pandas as pd
                q_scores = [e.get("score", 0) for e in evals]
                q_labels = [f"Q{i+1}: {e.get('skill', 'Topic')[:12]}" for i, e in enumerate(evals)]
                q_df = pd.DataFrame({"Technical Score": q_scores}, index=q_labels)
                st.bar_chart(q_df, height=200)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # TAB 3: SPEECH & COMMUNICATION ANALYSIS
    # -------------------------------------------------------------------------
    with tab_audio:
        st.subheader("🎙️ Spoken Speech Delivery & Articulation")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Pacing, filler words, and fluency metrics from your spoken answers (Maintained separately from technical correctness):</p>", unsafe_allow_html=True)
        
        tot_words = sum(a.get("word_count", 0) for a in audio_results.values())
        tot_fillers = sum(a.get("filler_words", 0) for a in audio_results.values())
        tot_pauses = sum(a.get("pauses", 0) for a in audio_results.values())
        valid_audios = [a for a in audio_results.values() if a.get("word_count", 0) > 0]
        avg_wpm = round(sum(a.get("words_per_minute", 0) for a in valid_audios) / max(1, len(valid_audios)), 1) if valid_audios else 0.0
        avg_fluency = round(sum(a.get("fluency_score", 0) for a in audio_results.values()) / max(1, len(audio_results)), 1) if audio_results else 0.0

        col_au1, col_au2, col_au3, col_au4 = st.columns(4)
        with col_au1:
            st.metric("Total Spoken Words", tot_words)
        with col_au2:
            st.metric("Average Speech Rate", f"{avg_wpm} WPM")
        with col_au3:
            st.metric("Detected Filler Words", tot_fillers)
        with col_au4:
            st.metric("Articulation Score", f"{avg_fluency} / 100")

        # Metric explanations in simple language
        render_html(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 16px 20px; margin-top: 14px;">
            <div style="color: #38bdf8; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">💡 How to Interpret Your Speech Metrics:</div>
            <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                • <strong>Speech Rate (WPM):</strong> Measures how many words you speak per minute. Typical conversational pace is 90-150 WPM. (Your session average: <strong>{avg_wpm} WPM</strong>).<br>
                • <strong>Filler Words:</strong> Counts hesitations like "um", "uh", "like", and "basically". Keeping fillers under 3 per session ensures strong verbal presence.<br>
                • <strong>Articulation / Fluency:</strong> A 0-100 score assessing pacing continuity and uninterrupted explanation flow within each 15-second window.<br>
                • <strong>Transcription Coverage:</strong> {len(valid_audios)} of {len(evals)} questions had speech successfully captured and transcribed.
            </div>
        </div>
        """)

        # Question-wise audio chart
        if audio_results:
            try:
                import pandas as pd
                audio_chart_dict = {
                    "WPM": [audio_results.get(i, {}).get("words_per_minute", 0) for i in range(len(evals))],
                    "Fluency Score": [audio_results.get(i, {}).get("fluency_score", 0) for i in range(len(evals))]
                }
                au_df = pd.DataFrame(audio_chart_dict, index=[f"Q{i+1}" for i in range(len(evals))])
                st.write("---")
                st.markdown("**Question-by-Question Speech Telemetry:**")
                st.bar_chart(au_df, height=200)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # TAB 4: FACIAL & VISUAL BEHAVIOUR
    # -------------------------------------------------------------------------
    with tab_vis:
        st.subheader("👁️ Facial, Eye-Gaze & Posture Analysis")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Landmark-based geometric estimations of camera presence, head pose, approximate gaze direction, and upper-body posture:</p>", unsafe_allow_html=True)

        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        with col_v1:
            st.metric("Face Visibility", f"{overall_vis.get('overall_face_visibility_pct', 0.0)}%")
        with col_v2:
            st.metric("Camera-Facing", f"{overall_vis.get('overall_camera_facing_pct', 0.0)}%")
        with col_v3:
            st.metric("Face Centering", f"{overall_vis.get('overall_face_centering_pct', 0.0)}%")
        with col_v4:
            st.metric("Head Movement", str(overall_vis.get('overall_head_movement', 'Natural'))[:12])
        with col_v5:
            st.metric("Posture Status", str(overall_vis.get('dominant_posture', 'Upright'))[:12])

        col_v_obs, col_v_sugg = st.columns(2)
        with col_v_obs:
            obs_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>• {obs}</div>" for obs in overall_vis.get("key_observations", [])])
            if not obs_items:
                obs_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>Maintaining natural camera presence.</div>"
            render_html(f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="color: #38bdf8; font-weight: 700; margin-bottom: 10px; font-size: 0.95rem;">👁️ Visual Engagement Observations</div>
                {obs_items}
            </div>
            """)

        with col_v_sugg:
            sugg_items = "".join([f"<div style='color: #e2e8f0; font-size: 0.88rem; margin-bottom: 6px;'>• {sg}</div>" for sg in overall_vis.get("improvement_suggestions", [])])
            if not sugg_items:
                sugg_items = "<div style='color: #94a3b8; font-size: 0.85rem;'>Good framing and posture.</div>"
            render_html(f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 12px; padding: 16px; height: 100%;">
                <div style="color: #c084fc; font-weight: 700; margin-bottom: 10px; font-size: 0.95rem;">📐 Framing & Pacing Suggestions</div>
                {sugg_items}
            </div>
            """)

        # Question-wise visual table & chart
        st.write("---")
        st.markdown("<div style='margin-bottom: 8px; font-weight: 700; color: #ffffff;'>📋 Question-Wise Visual Breakdown:</div>", unsafe_allow_html=True)
        q_vis_dict = st.session_state.get("technical_video_results", {})
        if q_vis_dict:
            vis_table_rows = []
            for q_idx in range(len(st.session_state.technical_questions)):
                qv = q_vis_dict.get(q_idx, {})
                q_num = q_idx + 1
                vis_table_rows.append({
                    "Question": f"Q{q_num}",
                    "Topic": qv.get("skill", "General"),
                    "Face Visibility": f"{qv.get('face_visibility_pct', 0.0)}%",
                    "Camera-Facing (Approx.)": f"{qv.get('gaze_summary', {}).get('approx_camera_facing_pct', 0.0)}%",
                    "Head Movement": qv.get("head_pose_summary", {}).get("movement_level", "Natural"),
                    "Posture": qv.get("posture_summary", {}).get("dominant_posture", "Upright"),
                    "Status": qv.get("visual_analysis_status", "Completed").capitalize()
                })
            st.table(vis_table_rows)

            try:
                import pandas as pd
                vis_chart_dict = {
                    "Visibility %": [q_vis_dict.get(i, {}).get("face_visibility_pct", 0) for i in range(len(evals))],
                    "Camera-Facing %": [q_vis_dict.get(i, {}).get("gaze_summary", {}).get("approx_camera_facing_pct", 0) for i in range(len(evals))]
                }
                v_df = pd.DataFrame(vis_chart_dict, index=[f"Q{i+1}" for i in range(len(evals))])
                st.bar_chart(v_df, height=180)
            except Exception:
                pass
        else:
            st.info("No webcam frames recorded for visual analysis in this session.")

        # Transparency disclaimer box
        render_html(f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 10px; padding: 12px 16px; margin-top: 14px;">
            <div style="color: #94a3b8; font-size: 0.82rem; line-height: 1.5;">
                ℹ️ <strong>Transparency Note:</strong> {overall_vis.get('disclaimer', 'Webcam eye-gaze and head-pose estimations reflect physical camera orientation. InterviewSense AI strictly avoids inferring personality, honesty, emotion, or intelligence from video recordings. Visual metrics do NOT alter technical correctness scores.')}
            </div>
        </div>
        """)

    # -------------------------------------------------------------------------
    # TAB 5: QUESTION-BY-QUESTION DETAILED EVALUATION
    # -------------------------------------------------------------------------
    with tab_questions:
        st.subheader("🔍 Question-by-Question Analysis")
        st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.2rem;'>Review each technical question, your submitted answer, multi-modal delivery indicators, scoring criteria, and model answer.</p>", unsafe_allow_html=True)

        for i, ev in enumerate(evals):
            q_sc = ev.get("score", 0)
            q_class = classify_performance(q_sc)
            q_badge_color = "#4ade80" if q_sc >= 75 else "#facc15" if q_sc >= 50 else "#f87171"

            expander_title = f"Q{i+1}: {ev.get('question')} — [Score: {q_sc}/100 • {q_class}]"
            
            with st.expander(expander_title, expanded=(i == 0)):
                # Metadata Tags
                render_html(f"""
                <div style="margin-bottom: 12px;">
                    <span class="meta-tag meta-tag-domain">{ev.get('domain', '')}</span>
                    <span class="meta-tag meta-tag-skill">{ev.get('skill', '')}</span>
                    <span class="meta-tag meta-tag-diff">{ev.get('difficulty', '')}</span>
                    <span class="meta-tag meta-tag-type">{ev.get('question_type', '')}</span>
                    <span style="display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; color: {q_badge_color}; background: rgba(15, 23, 42, 0.8); border: 1px solid {q_badge_color};">
                        Score: {q_sc}/100
                    </span>
                </div>
                """)

                # Multi-Modal Delivery Summary (Visual + Audio)
                q_v_info = st.session_state.get("technical_video_results", {}).get(i, {})
                q_a_info = st.session_state.get("technical_audio_results", {}).get(i, {})
                v_vis_disp = f"{q_v_info.get('face_visibility_pct', 0.0)}%"
                v_cam_disp = f"{q_v_info.get('gaze_summary', {}).get('approx_camera_facing_pct', 0.0)}%"
                a_wpm_disp = f"{q_a_info.get('words_per_minute', 0.0)} WPM"
                a_fil_disp = f"{q_a_info.get('filler_words', 0)} fillers"

                render_html(f"""
                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 8px 14px; margin-bottom: 12px; font-size: 0.83rem; display: flex; flex-wrap: wrap; justify-content: space-between;">
                    <span style="color: #7dd3fc;">👁️ <strong>Visual:</strong> {v_vis_disp} visibility • {v_cam_disp} camera-facing (approx.)</span>
                    <span style="color: #c084fc;">🎙️ <strong>Audio:</strong> {a_wpm_disp} • {a_fil_disp}</span>
                </div>
                """)

                # Criteria Breakdown Grid
                crit = ev.get("criteria_scores", {})
                render_html(f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
                    <div style="color: #38bdf8; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 8px;">Criteria Breakdown:</div>
                    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; text-align: center;">
                        <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                            <div style="color: #94a3b8; font-size: 0.75rem;">Correctness</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('technical_correctness', 0)} / 40</div>
                        </div>
                        <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                            <div style="color: #94a3b8; font-size: 0.75rem;">Concepts</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('conceptual_understanding', 0)} / 25</div>
                        </div>
                        <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                            <div style="color: #94a3b8; font-size: 0.75rem;">Relevance</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('relevance', 0)} / 15</div>
                        </div>
                        <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                            <div style="color: #94a3b8; font-size: 0.75rem;">Completeness</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('completeness', 0)} / 15</div>
                        </div>
                        <div style="background: rgba(2, 6, 23, 0.6); padding: 8px; border-radius: 6px;">
                            <div style="color: #94a3b8; font-size: 0.75rem;">Quality</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.95rem;">{crit.get('explanation_quality', 0)} / 5</div>
                        </div>
                    </div>
                </div>
                """)

                # Candidate's Submitted Response (Read-Only Styled Interface)
                st.markdown("**Your Submitted Response:**")
                if ev.get("is_unanswered"):
                    render_html("""
                    <div style="background: rgba(251, 146, 60, 0.08); border: 1px solid rgba(251, 146, 60, 0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; color: #fb923c; font-size: 0.92rem;">
                        ⚠️ <em>No answer was submitted for this question (Score: 0/100)</em>
                    </div>
                    """)
                else:
                    ans_text_raw = ev.get("candidate_answer", "")
                    escaped_ans = html.escape(ans_text_raw).replace("\n", "<br>")
                    render_html(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; color: #f1f5f9; font-size: 0.92rem; line-height: 1.55;">
                        {escaped_ans}
                    </div>
                    """)

                # Detailed Feedback Sections
                col_fb1, col_fb2 = st.columns(2)
                with col_fb1:
                    st.markdown("<div style='color: #4ade80; font-weight: 700; margin-bottom: 6px;'>✅ What You Did Well:</div>", unsafe_allow_html=True)
                    for item in ev.get("what_you_did_well", []):
                        st.write(f"- {item}")

                    st.markdown("<div style='color: #fb923c; font-weight: 700; margin-top: 14px; margin-bottom: 6px;'>⚠️ Missing Points:</div>", unsafe_allow_html=True)
                    for item in ev.get("missing_points", []):
                        st.write(f"- {item}")

                with col_fb2:
                    st.markdown("<div style='color: #38bdf8; font-weight: 700; margin-bottom: 6px;'>💡 Areas to Improve:</div>", unsafe_allow_html=True)
                    for item in ev.get("areas_to_improve", []):
                        st.write(f"- {item}")

                    st.markdown("<div style='color: #c084fc; font-weight: 700; margin-top: 14px; margin-bottom: 6px;'>📝 Final Assessment:</div>", unsafe_allow_html=True)
                    st.markdown(f"*{ev.get('final_evaluation', '')}*")

                # Suggested Model Answer
                st.write("---")
                st.markdown("<div style='color: #7dd3fc; font-weight: 700; font-size: 0.92rem; margin-bottom: 6px;'>📘 Suggested Model Answer:</div>", unsafe_allow_html=True)
                model_ans_escaped = html.escape(ev.get('suggested_answer', '')).replace("\n", "<br>")
                render_html(f"""
                <div style="background: rgba(15, 23, 42, 0.9); border-left: 4px solid #38bdf8; padding: 14px 18px; border-radius: 6px; color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">
                    {model_ans_escaped}
                </div>
                """)

    st.write("---")

    # -------------------------------------------------------------------------
    # SECTION C: DOWNLOADABLE PDF REPORT & NAVIGATION
    # -------------------------------------------------------------------------
    try:
        session_meta = {
            "candidate_name": candidate_name,
            "domain": st.session_state.technical_domain,
            "skills": st.session_state.technical_skills,
            "difficulty": st.session_state.technical_difficulty,
            "total_questions": results["total_questions"],
            "timestamp": interview_timestamp,
            "audio_analysis": audio_results,
            "visual_analysis": overall_vis,
            "question_visual_results": st.session_state.get("technical_video_results", {}),
            "combined_summary": combined_summary,
            "improvement_roadmap": roadmap
        }
        pdf_bytes = generate_technical_pdf_report(session_meta, results)
        clean_domain_name = re.sub(r'[^a-zA-Z0-9_]', '_', st.session_state.technical_domain)
        pdf_filename = f"InterviewSense_Report_{clean_domain_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        col_d1, col_d2 = st.columns([1.5, 2.5])
        with col_d1:
            st.download_button(
                label="📥 Download Technical Report (PDF)",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                key="btn_download_tech_pdf",
                type="primary",
                use_container_width=True
            )
        with col_d2:
            st.caption("📄 Download your comprehensive technical performance evaluation report containing score breakdowns, question analyses, model answers, and improvement recommendations.")
    except Exception as e:
        st.warning(f"Report generation note: PDF could not be created ({e}). You can still review your full results above.")

    st.write("---")

    # Navigation and Restart
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🔄 Retake Technical Interview", key="btn_retake_tech_interview", type="primary", use_container_width=True):
            # Clean up temporary audio files from previous session
            cleanup_temp_audio(st.session_state.get('technical_session_id'))
            st.session_state.technical_session_id = uuid.uuid4().hex[:10]
            st.session_state.technical_audio_files = {}
            st.session_state.technical_transcripts = {}
            st.session_state.technical_raw_transcripts = {}
            # Cleanly reset only technical interview session variables
            st.session_state.technical_questions = []
            st.session_state.technical_question_index = 0
            st.session_state.technical_answers = {}
            st.session_state.technical_frames = {}
            st.session_state.technical_video_results = {}
            st.session_state.technical_audio_results = {}
            st.session_state.technical_overall_visual_analysis = None
            st.session_state.technical_interview_completed = False
            st.session_state.technical_interview_submitted = False
            st.session_state.confirm_end_technical = False
            st.session_state.confirm_submit_technical = False
            st.session_state.technical_evaluation_results = None
            st.session_state.technical_overall_score = 0
            st.session_state.technical_performance_level = "Needs Improvement"
            st.session_state.technical_evaluation_completed = False
            for k in list(st.session_state.keys()):
                if any(k.startswith(prefix) for prefix in [
                    "tech_ans_input_", "voice_dur_", "tech_spoken_",
                    "tech_countdown_done_", "sub_edit_ans_", "text_area_q_"
                ]):
                    del st.session_state[k]
            st.session_state.current_page = 'technical_setup'
            st.rerun()

    with col_nav2:
        if st.button("🏠 Back to Home", key="btn_back_to_home_from_results", type="secondary", use_container_width=True):
            st.session_state.current_page = 'landing'
            st.session_state.current_tab = 'Home'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# Backward-compatibility alias
render_technical_analysis_page = render_technical_results_page


