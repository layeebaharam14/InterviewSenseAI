"""
technical_report_pdf.py
Comprehensive Multi-Page PDF Report Generation Module for InterviewSense AI.
Generates structured, professional technical interview performance reports using PyMuPDF (fitz).

Contains:
1. Cover & Interview Information (Candidate, Domain, Skills, Date, Completion Status)
2. Executive Summary & Overall Technical Performance (Radial Score, Classification)
3. Criteria Breakdown (Correctness, Concepts, Relevance, Completeness, Quality)
4. Skill-Wise & Difficulty-Wise Performance
5. Speech and Communication Delivery Analysis (WPM, Fillers, Pauses, Fluency)
6. Facial, Eye-Gaze and Posture Behavioural Analysis (Disclaimers & Limitations)
7. Combined Performance Synthesis & Question Breakdown Table
8. Personalised Improvement Roadmap (High Priority, Medium Priority, Further Practice)
9. Question-by-Question Detailed Evaluation with dynamic multi-page flow
10. Methodology, Rubrics, and Scientific Limitations
"""

import io
import re
from datetime import datetime
from typing import Dict, Any, List
import pymupdf as fitz

from src.interviewsense.analysis.technical_evaluation import generate_combined_summary, generate_improvement_roadmap

def sanitize_text(text: Any) -> str:
    """
    Sanitizes text by replacing unicode characters with clean ASCII/Latin-1 equivalents
    to prevent PDF font glyph encoding errors in standard Helvetica.
    """
    if text is None:
        return ""
    text = str(text).strip()
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--", "\u2026": "...",
        "\u2022": "*", "\u25aa": "*", "\u25cf": "*", "\u2713": "[OK]",
        "\u2714": "[OK]", "\u2717": "[X]", "\u2718": "[X]",
        "\u2192": "->", "\u2190": "<-", "\u21d2": "=>",
        "\u26a0": "[!]", "\u00a0": " ", "\u200b": ""
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Filter characters outside latin-1
    return "".join(c if ord(c) < 256 else " " for c in text)

def truncate_text(text: str, max_chars: int = 400) -> str:
    """Safely truncates long text blocks for PDF display."""
    if not text:
        return ""
    text = sanitize_text(text)
    if len(text) > max_chars:
        return text[:max_chars - 3] + "..."
    return text

def generate_technical_pdf_report(session_summary: Dict[str, Any], evaluation_results: Dict[str, Any]) -> bytes:
    """
    Generates a structured, multi-page PDF performance report for a Technical Interview session.

    Parameters:
        session_summary: Metadata dict with candidate_name, domain, skills, difficulty,
                         total_questions, visual_analysis, audio_analysis, etc.
        evaluation_results: Results dict from technical_evaluation.evaluate_technical_interview.

    Returns:
        bytes: Binary PDF content.
    """
    doc = fitz.open()
    width, height = 595, 842  # A4 Dimensions in points
    margin_left = 36
    margin_right = 559
    usable_width = margin_right - margin_left

    # Color palette (RGB normalized 0.0 - 1.0)
    COLOR_PRIMARY = (0.04, 0.07, 0.13)      # Dark Navy #0b1120
    COLOR_CYAN = (0.22, 0.74, 0.97)         # Cyan #38bdf8
    COLOR_WHITE = (1.0, 1.0, 1.0)           # White
    COLOR_GRAY_DARK = (0.2, 0.25, 0.35)     # Dark Gray
    COLOR_GRAY_LIGHT = (0.94, 0.96, 0.98)   # Light Gray Background
    COLOR_BORDER = (0.8, 0.85, 0.9)         # Border Gray
    COLOR_TEXT = (0.1, 0.15, 0.2)           # Main text
    COLOR_TEXT_MUTED = (0.4, 0.45, 0.55)    # Muted text
    COLOR_GREEN = (0.13, 0.77, 0.37)        # Emerald
    COLOR_AMBER = (0.98, 0.76, 0.08)        # Amber
    COLOR_ORANGE = (0.98, 0.57, 0.23)       # Orange
    COLOR_RED = (0.94, 0.27, 0.27)          # Red

    overall_sc = evaluation_results.get("overall_score", 0)
    perf_level = evaluation_results.get("performance_level", "Good")
    
    # Classification color
    if perf_level == "Excellent":
        perf_color = COLOR_GREEN
    elif perf_level == "Very Good":
        perf_color = COLOR_CYAN
    elif perf_level == "Good":
        perf_color = COLOR_AMBER
    elif perf_level == "Needs Improvement":
        perf_color = COLOR_ORANGE
    else:
        perf_color = COLOR_RED

    evals = evaluation_results.get("evaluations", [])
    tot_evals = max(len(evals), 1)

    # Audio and Visual extractions
    audio_results = session_summary.get("audio_analysis", {})
    if not isinstance(audio_results, dict):
        audio_results = {}
    video_summary = session_summary.get("visual_analysis", {})
    if not isinstance(video_summary, dict):
        video_summary = {}
    q_vis_results = session_summary.get("question_visual_results", {})
    if not isinstance(q_vis_results, dict):
        q_vis_results = {}

    # Combined summary and roadmap
    combined_summary = session_summary.get("combined_summary")
    if not combined_summary:
        combined_summary = generate_combined_summary(evaluation_results, audio_results, video_summary)
    
    roadmap = session_summary.get("improvement_roadmap")
    if not roadmap:
        roadmap = generate_improvement_roadmap(evaluation_results, audio_results, video_summary)

    candidate_name = sanitize_text(session_summary.get("candidate_name") or "Candidate")
    timestamp = sanitize_text(session_summary.get("timestamp", datetime.now().strftime("%B %d, %Y - %I:%M %p")))
    domain_text = sanitize_text(str(session_summary.get("domain", "General Technical")))
    difficulty_text = sanitize_text(str(session_summary.get("difficulty", "Intermediate")))
    skills_list = [sanitize_text(s) for s in session_summary.get("skills", [])]
    skills_str = ", ".join(skills_list) if skills_list else "General Domain Topics"

    # =========================================================================
    # PAGE 1: COVER & EXECUTIVE TECHNICAL PERFORMANCE SUMMARY
    # =========================================================================
    page1 = doc.new_page(width=width, height=height)

    # Top Header Banner
    page1.draw_rect(fitz.Rect(0, 0, width, 80), color=None, fill=COLOR_PRIMARY)
    page1.insert_text((margin_left, 32), "INTERVIEWSENSE AI", fontsize=15, color=COLOR_CYAN, fontname="helv")
    page1.insert_text((margin_left, 52), "Technical Interview Performance & Analytics Report", fontsize=11, color=COLOR_WHITE, fontname="helv")
    page1.insert_text((margin_left, 68), f"Candidate: {candidate_name}  |  Session Date: {timestamp}", fontsize=8.5, color=(0.7, 0.8, 0.9), fontname="helv")
    page1.insert_text((width - 150, 48), "STATUS: COMPLETED", fontsize=9, color=COLOR_GREEN, fontname="helv")

    y = 96

    # Overall Score Box
    score_box_height = 84
    page1.draw_rect(fitz.Rect(margin_left, y, margin_right, y + score_box_height), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=1)
    
    page1.insert_text((margin_left + 18, y + 24), "OVERALL TECHNICAL SCORE", fontsize=9.5, color=COLOR_TEXT_MUTED, fontname="helv")
    page1.insert_text((margin_left + 18, y + 64), f"{overall_sc}", fontsize=36, color=COLOR_PRIMARY, fontname="helv")
    page1.insert_text((margin_left + 78, y + 56), "/ 100", fontsize=14, color=COLOR_TEXT_MUTED, fontname="helv")

    # Classification Badge
    page1.draw_rect(fitz.Rect(margin_left + 145, y + 22, margin_left + 325, y + 56), color=None, fill=COLOR_PRIMARY)
    page1.insert_text((margin_left + 160, y + 43), f"Level: {perf_level}", fontsize=11.5, color=perf_color, fontname="helv")

    # Right Column Summary in Score Box
    page1.insert_text((margin_left + 345, y + 24), f"Domain: {truncate_text(domain_text, 28)}", fontsize=8.5, color=COLOR_TEXT, fontname="helv")
    page1.insert_text((margin_left + 345, y + 42), f"Difficulty: {difficulty_text}", fontsize=8.5, color=COLOR_TEXT, fontname="helv")
    page1.insert_text((margin_left + 345, y + 60), f"Questions: {evaluation_results.get('answered_questions', 0)} Answered / {evaluation_results.get('total_questions', 0)} Total", fontsize=8.5, color=COLOR_TEXT, fontname="helv")

    y += score_box_height + 20

    # Section 1: Evaluation Criteria Scores
    page1.insert_text((margin_left, y), "EVALUATION CRITERIA BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    avg_correctness = round(sum(e.get("criteria_scores", {}).get("technical_correctness", 0) for e in evals) / tot_evals, 1)
    avg_concepts = round(sum(e.get("criteria_scores", {}).get("conceptual_understanding", 0) for e in evals) / tot_evals, 1)
    avg_relevance = round(sum(e.get("criteria_scores", {}).get("relevance", 0) for e in evals) / tot_evals, 1)
    avg_completeness = round(sum(e.get("criteria_scores", {}).get("completeness", 0) for e in evals) / tot_evals, 1)
    avg_quality = round(sum(e.get("criteria_scores", {}).get("explanation_quality", 0) for e in evals) / tot_evals, 1)

    crit_data = [
        ("Technical Correctness", f"{avg_correctness} / 40", f"{int((avg_correctness / 40) * 100)}%"),
        ("Conceptual Understanding", f"{avg_concepts} / 25", f"{int((avg_concepts / 25) * 100)}%"),
        ("Relevance", f"{avg_relevance} / 15", f"{int((avg_relevance / 15) * 100)}%"),
        ("Completeness", f"{avg_completeness} / 15", f"{int((avg_completeness / 15) * 100)}%"),
        ("Explanation Quality", f"{avg_quality} / 5", f"{int((avg_quality / 5) * 100)}%"),
    ]

    col_w = usable_width / 5
    for idx, (c_name, c_score, c_pct) in enumerate(crit_data):
        box_x = margin_left + idx * col_w
        page1.draw_rect(fitz.Rect(box_x, y, box_x + col_w - 6, y + 48), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
        page1.insert_textbox(fitz.Rect(box_x + 3, y + 4, box_x + col_w - 9, y + 22), c_name, fontsize=7.5, color=COLOR_TEXT_MUTED, align=1)
        page1.insert_text((box_x + 6, y + 36), c_score, fontsize=9.5, color=COLOR_PRIMARY, fontname="helv")
        page1.insert_text((box_x + col_w - 38, y + 36), c_pct, fontsize=8, color=COLOR_CYAN, fontname="helv")

    y += 64

    # Section 2: Skill-wise Performance Breakdown
    page1.insert_text((margin_left, y), "SKILL-WISE PERFORMANCE BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    skill_avgs = evaluation_results.get("skill_averages", {})
    if skill_avgs:
        for sk_name, sk_score in list(skill_avgs.items())[:4]:
            sk_level = "Excellent" if sk_score >= 90 else "Very Good" if sk_score >= 75 else "Good" if sk_score >= 60 else "Needs Improvement" if sk_score >= 40 else "Poor"
            page1.insert_text((margin_left + 8, y + 10), truncate_text(sk_name, 35), fontsize=8.5, color=COLOR_TEXT, fontname="helv")
            page1.insert_text((margin_left + 310, y + 10), f"Score: {sk_score}/100", fontsize=8.5, color=COLOR_PRIMARY, fontname="helv")
            page1.insert_text((margin_left + 430, y + 10), f"Level: {sk_level}", fontsize=8.5, color=COLOR_TEXT_MUTED, fontname="helv")
            
            bar_y = y + 14
            page1.draw_line(fitz.Point(margin_left + 8, bar_y), fitz.Point(margin_left + 500, bar_y), color=(0.9, 0.92, 0.95), width=3)
            fill_width = margin_left + 8 + (492 * (min(100.0, sk_score) / 100.0))
            page1.draw_line(fitz.Point(margin_left + 8, bar_y), fitz.Point(fill_width, bar_y), color=COLOR_CYAN, width=3)
            y += 22
    else:
        page1.insert_text((margin_left + 8, y + 12), "No skill data evaluated.", fontsize=8.5, color=COLOR_TEXT_MUTED)
        y += 18

    # Section 3: Difficulty-wise Performance Breakdown
    y += 10
    page1.insert_text((margin_left, y), "DIFFICULTY-WISE PERFORMANCE BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    diff_avgs = evaluation_results.get("difficulty_averages", {})
    if diff_avgs:
        col_dw = usable_width / max(1, len(diff_avgs))
        for idx, (df_name, df_score) in enumerate(diff_avgs.items()):
            bx = margin_left + idx * col_dw
            page1.draw_rect(fitz.Rect(bx, y, bx + col_dw - 8, y + 36), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
            page1.insert_text((bx + 8, y + 15), f"Tier: {df_name}", fontsize=8, color=COLOR_TEXT_MUTED, fontname="helv")
            page1.insert_text((bx + 8, y + 28), f"Avg Score: {df_score}/100", fontsize=9, color=COLOR_PRIMARY, fontname="helv")
        y += 48
    else:
        page1.insert_text((margin_left + 8, y + 12), "No difficulty tier breakdown available.", fontsize=8.5, color=COLOR_TEXT_MUTED)
        y += 24

    # Section 4: Executive Technical Summary & Skills Covered
    y += 6
    page1.insert_text((margin_left, y), "EXECUTIVE ASSESSMENT & SKILLS SUMMARY", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    page1.draw_rect(fitz.Rect(margin_left, y, margin_right, y + 80), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page1.insert_text((margin_left + 10, y + 16), f"Primary Skills Evaluated: {truncate_text(skills_str, 80)}", fontsize=8.5, color=COLOR_PRIMARY, fontname="helv")
    page1.insert_text((margin_left + 10, y + 32), f"Strongest Technical Area: {evaluation_results.get('strongest_skill', 'N/A')}", fontsize=8.5, color=COLOR_GREEN, fontname="helv")
    page1.insert_text((margin_left + 10, y + 48), f"Primary Revision Focus: {evaluation_results.get('weakest_skill', 'N/A')}", fontsize=8.5, color=COLOR_ORANGE, fontname="helv")
    exec_summary_text = (
        f"Candidate completed {evaluation_results.get('answered_questions', 0)} of {evaluation_results.get('total_questions', 0)} "
        f"technical questions at {difficulty_text} difficulty, demonstrating {perf_level.lower()} mastery across the evaluated competencies."
    )
    page1.insert_textbox(fitz.Rect(margin_left + 10, y + 54, margin_right - 10, y + 76), exec_summary_text, fontsize=8, color=COLOR_TEXT_MUTED)

    # Footer Page 1
    page1.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page1.insert_text((margin_left, height - 22), "InterviewSense AI -- Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)

    # =========================================================================
    # PAGE 2: SPEECH, COMMUNICATION & VISUAL BEHAVIOURAL ANALYSIS
    # =========================================================================
    page2 = doc.new_page(width=width, height=height)

    # Top Header Banner
    page2.draw_rect(fitz.Rect(0, 0, width, 55), color=None, fill=COLOR_PRIMARY)
    page2.insert_text((margin_left, 32), "SPEECH, COMMUNICATION & VISUAL BEHAVIOURAL ANALYSIS", fontsize=12, color=COLOR_CYAN, fontname="helv")
    page2.insert_text((margin_left, 46), "Multi-Modal Spoken Fluency and Landmark-Based Physical Engagement Metrics", fontsize=8.5, color=COLOR_WHITE, fontname="helv")

    y2 = 72

    # Section A: Speech & Communication Delivery
    page2.insert_text((margin_left, y2), "A. SPOKEN SPEECH DELIVERY & ARTICULATION", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page2.draw_line(fitz.Point(margin_left, y2 + 4), fitz.Point(margin_right, y2 + 4), color=COLOR_CYAN, width=1.5)
    y2 += 16

    tot_words = sum(a.get("word_count", 0) for a in audio_results.values()) if audio_results else 0
    tot_fillers = sum(a.get("filler_words", 0) for a in audio_results.values()) if audio_results else 0
    valid_aud = [a for a in audio_results.values() if a.get("word_count", 0) > 0]
    avg_wpm = round(sum(a.get("words_per_minute", 0) for a in valid_aud) / max(1, len(valid_aud)), 1) if valid_aud else 0.0
    avg_fluency = round(sum(a.get("fluency_score", 0) for a in audio_results.values()) / max(1, len(audio_results)), 1) if audio_results else 0.0

    speech_cards = [
        ("Total Spoken Words", f"{tot_words}", "15s per question"),
        ("Speaking Rate", f"{avg_wpm} WPM", "Target: 90-150 WPM"),
        ("Filler Words", f"{tot_fillers}", "Um, uh, like, etc."),
        ("Fluency Score", f"{avg_fluency} / 100", "Pacing & continuity")
    ]
    col_sw = usable_width / 4
    for idx, (m_title, m_val, m_sub) in enumerate(speech_cards):
        bx = margin_left + idx * col_sw
        page2.draw_rect(fitz.Rect(bx, y2, bx + col_sw - 6, y2 + 48), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=0.8)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 4, bx + col_sw - 10, y2 + 18), m_title, fontsize=7.5, color=COLOR_TEXT_MUTED, align=1)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 20, bx + col_sw - 10, y2 + 34), m_val, fontsize=10.5, color=COLOR_PRIMARY, align=1)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 34, bx + col_sw - 10, y2 + 46), m_sub, fontsize=6.5, color=COLOR_CYAN, align=1)

    y2 += 62

    # Section B: Visual Behavioural Analysis
    page2.insert_text((margin_left, y2), "B. FACIAL, EYE-GAZE AND POSTURE BEHAVIOURAL ANALYSIS", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page2.draw_line(fitz.Point(margin_left, y2 + 4), fitz.Point(margin_right, y2 + 4), color=COLOR_CYAN, width=1.5)
    y2 += 16

    face_vis_pct = video_summary.get("overall_face_visibility_pct", 0.0)
    cam_facing_pct = video_summary.get("overall_camera_facing_pct", 0.0)
    centering_pct = video_summary.get("overall_face_centering_pct", 0.0)
    movement_str = str(video_summary.get("overall_head_movement", "Natural"))
    posture_str = str(video_summary.get("dominant_posture", "Upright"))

    vis_cards = [
        ("Face Visibility", f"{face_vis_pct}%", "In camera frame"),
        ("Camera-Facing", f"{cam_facing_pct}%", "Approx. eye gaze"),
        ("Face-Centering", f"{centering_pct}%", "In central zone"),
        ("Head Movement", truncate_text(movement_str, 12), "Pacing / stability"),
        ("Posture", truncate_text(posture_str, 12), "Shoulder alignment")
    ]
    col_vw = usable_width / 5
    for idx, (m_title, m_val, m_sub) in enumerate(vis_cards):
        bx = margin_left + idx * col_vw
        page2.draw_rect(fitz.Rect(bx, y2, bx + col_vw - 6, y2 + 48), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=0.8)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 4, bx + col_vw - 10, y2 + 18), m_title, fontsize=7.5, color=COLOR_TEXT_MUTED, align=1)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 20, bx + col_vw - 10, y2 + 34), m_val, fontsize=10.5, color=COLOR_PRIMARY, align=1)
        page2.insert_textbox(fitz.Rect(bx + 4, y2 + 34, bx + col_vw - 10, y2 + 46), m_sub, fontsize=6.5, color=COLOR_CYAN, align=1)

    y2 += 62

    # Observations & Suggestions
    col_w_half = (usable_width - 12) / 2
    # Left: Observations
    page2.draw_rect(fitz.Rect(margin_left, y2, margin_left + col_w_half, y2 + 115), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page2.insert_text((margin_left + 10, y2 + 16), "KEY DELIVERY & VISUAL OBSERVATIONS", fontsize=8.5, color=COLOR_PRIMARY, fontname="helv")
    obs_list = combined_summary.get("visual_observations", [])
    o_y = y2 + 28
    for obs in obs_list[:4]:
        page2.insert_textbox(fitz.Rect(margin_left + 10, o_y, margin_left + col_w_half - 10, o_y + 20), f"- {sanitize_text(obs)}", fontsize=7.5, color=COLOR_TEXT)
        o_y += 20

    # Right: Framing & Communication Suggestions
    right_x = margin_left + col_w_half + 12
    page2.draw_rect(fitz.Rect(right_x, y2, margin_right, y2 + 115), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page2.insert_text((right_x + 10, y2 + 16), "FRAMING & COMMUNICATION SUGGESTIONS", fontsize=8.5, color=COLOR_CYAN, fontname="helv")
    sugg_list = combined_summary.get("communication_improvements", [])
    if video_summary.get("improvement_suggestions"):
        sugg_list = sugg_list + video_summary.get("improvement_suggestions", [])
    s_y = y2 + 28
    for sg in sugg_list[:4]:
        page2.insert_textbox(fitz.Rect(right_x + 10, s_y, margin_right - 10, s_y + 20), f"- {sanitize_text(sg)}", fontsize=7.5, color=COLOR_TEXT)
        s_y += 20

    y2 += 128

    # Section: Question-wise Multi-Modal Breakdown Table
    page2.insert_text((margin_left, y2), "QUESTION-WISE MULTI-MODAL BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page2.draw_line(fitz.Point(margin_left, y2 + 4), fitz.Point(margin_right, y2 + 4), color=COLOR_CYAN, width=1.5)
    y2 += 16

    # Table Header
    page2.draw_rect(fitz.Rect(margin_left, y2, margin_right, y2 + 18), color=None, fill=COLOR_GRAY_LIGHT)
    page2.insert_text((margin_left + 8, y2 + 12), "Q#", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    page2.insert_text((margin_left + 35, y2 + 12), "Topic / Skill", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    page2.insert_text((margin_left + 180, y2 + 12), "Spoken Words", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    page2.insert_text((margin_left + 265, y2 + 12), "Speech Rate", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    page2.insert_text((margin_left + 355, y2 + 12), "Visibility %", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    page2.insert_text((margin_left + 440, y2 + 12), "Camera-Facing %", fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
    y2 += 22

    tot_q = session_summary.get("total_questions", len(evals))
    for q_i in range(tot_q):
        q_v = q_vis_results.get(q_i, {})
        q_a = audio_results.get(q_i, {})
        v_skill = truncate_text(q_v.get("skill") or (evals[q_i].get("skill") if q_i < len(evals) else "Topic"), 22)
        a_words = f"{q_a.get('word_count', 0)} words"
        a_wpm = f"{q_a.get('words_per_minute', 0.0)} WPM"
        v_vis = f"{q_v.get('face_visibility_pct', 0.0)}%"
        v_cam = f"{q_v.get('gaze_summary', {}).get('approx_camera_facing_pct', 0.0)}%"

        bg_row = COLOR_WHITE if q_i % 2 == 0 else COLOR_GRAY_LIGHT
        page2.draw_rect(fitz.Rect(margin_left, y2, margin_right, y2 + 16), color=None, fill=bg_row)
        page2.insert_text((margin_left + 8, y2 + 12), f"Q{q_i + 1}", fontsize=7.5, color=COLOR_TEXT, fontname="helv")
        page2.insert_text((margin_left + 35, y2 + 12), v_skill, fontsize=7.5, color=COLOR_TEXT, fontname="helv")
        page2.insert_text((margin_left + 185, y2 + 12), a_words, fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
        page2.insert_text((margin_left + 270, y2 + 12), a_wpm, fontsize=7.5, color=COLOR_CYAN, fontname="helv")
        page2.insert_text((margin_left + 360, y2 + 12), v_vis, fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
        page2.insert_text((margin_left + 445, y2 + 12), v_cam, fontsize=7.5, color=COLOR_CYAN, fontname="helv")
        y2 += 18

    y2 += 12

    # Limitations & Pseudoscience Disclaimer Box
    page2.draw_rect(fitz.Rect(margin_left, y2, margin_right, y2 + 55), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page2.insert_text((margin_left + 10, y2 + 14), "IMPORTANT TRANSPARENCY DISCLAIMER & SCIENTIFIC LIMITATIONS", fontsize=8, color=COLOR_TEXT_MUTED, fontname="helv")
    disclaimer_text = (
        "Webcam eye-gaze and head-pose estimations reflect physical camera orientation and framing. "
        "InterviewSense AI strictly avoids inferring personality, honesty, emotion, or intelligence from video recordings. "
        "Speech and visual metrics are presented as separate coaching indicators and do NOT alter technical correctness scores."
    )
    page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 18, margin_right - 10, y2 + 50), disclaimer_text, fontsize=7.5, color=COLOR_TEXT_MUTED)

    # Footer Page 2
    page2.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page2.insert_text((margin_left, height - 22), "InterviewSense AI -- Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)

    # =========================================================================
    # PAGE 3: COMBINED PERFORMANCE SUMMARY & PERSONALISED ROADMAP
    # =========================================================================
    page3 = doc.new_page(width=width, height=height)

    # Top Header Banner
    page3.draw_rect(fitz.Rect(0, 0, width, 55), color=None, fill=COLOR_PRIMARY)
    page3.insert_text((margin_left, 32), "COMBINED PERFORMANCE SUMMARY & PERSONALISED ROADMAP", fontsize=12, color=COLOR_CYAN, fontname="helv")
    page3.insert_text((margin_left, 46), "Prioritized Action Plan Grounded Strictly in Evaluated Performance", fontsize=8.5, color=COLOR_WHITE, fontname="helv")

    y3 = 72

    # Strengths vs Areas to Improve
    page3.insert_text((margin_left, y3), "SYNTHESIZED STRENGTHS & FOCUS AREAS", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page3.draw_line(fitz.Point(margin_left, y3 + 4), fitz.Point(margin_right, y3 + 4), color=COLOR_CYAN, width=1.5)
    y3 += 16

    col_h3 = 110
    # Left Box: Strengths
    page3.draw_rect(fitz.Rect(margin_left, y3, margin_left + col_w_half, y3 + col_h3), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page3.insert_text((margin_left + 10, y3 + 16), "KEY TECHNICAL & DELIVERY STRENGTHS", fontsize=8.5, color=(0.1, 0.6, 0.3), fontname="helv")
    str_items = combined_summary.get("technical_strengths", []) + combined_summary.get("communication_strengths", [])
    sy3 = y3 + 26
    for st_text in str_items[:4]:
        page3.insert_textbox(fitz.Rect(margin_left + 10, sy3, margin_left + col_w_half - 10, sy3 + 18), f"[OK] {sanitize_text(st_text)}", fontsize=7.5, color=COLOR_TEXT)
        sy3 += 20

    # Right Box: Weaknesses
    page3.draw_rect(fitz.Rect(right_x, y3, margin_right, y3 + col_h3), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page3.insert_text((right_x + 10, y3 + 16), "PRIMARY AREAS REQUIRING REVISION", fontsize=8.5, color=(0.85, 0.45, 0.1), fontname="helv")
    imp_items = combined_summary.get("weak_technical_areas", []) + combined_summary.get("communication_improvements", [])
    iy3 = y3 + 26
    for imp_text in imp_items[:4]:
        page3.insert_textbox(fitz.Rect(right_x + 10, iy3, margin_right - 10, iy3 + 18), f"[!] {sanitize_text(imp_text)}", fontsize=7.5, color=COLOR_TEXT)
        iy3 += 20

    y3 += col_h3 + 18

    # Personalised Improvement Roadmap Section
    page3.insert_text((margin_left, y3), "PERSONALISED IMPROVEMENT ROADMAP", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page3.draw_line(fitz.Point(margin_left, y3 + 4), fitz.Point(margin_right, y3 + 4), color=COLOR_CYAN, width=1.5)
    y3 += 16

    roadmap_tiers = [
        ("HIGH PRIORITY ACTIONS", roadmap.get("high_priority", []), (0.9, 0.25, 0.25), "Immediate focus: Core mechanics and unaddressed topics"),
        ("MEDIUM PRIORITY ACTIONS", roadmap.get("medium_priority", []), (0.95, 0.55, 0.15), "Secondary focus: Depth, edge cases, and pacing calibration"),
        ("FURTHER PRACTICE & EXTENSION", roadmap.get("further_practice", []), (0.1, 0.65, 0.35), "Long-term mastery: Distributed systems and framing presence")
    ]

    for tier_title, items, tier_color, tier_desc in roadmap_tiers:
        page3.draw_rect(fitz.Rect(margin_left, y3, margin_right, y3 + 18), color=None, fill=COLOR_PRIMARY)
        page3.insert_text((margin_left + 8, y3 + 13), tier_title, fontsize=8, color=COLOR_CYAN, fontname="helv")
        page3.insert_text((margin_left + 175, y3 + 13), f"-- {tier_desc}", fontsize=7.5, color=COLOR_WHITE, fontname="helv")
        y3 += 22

        if items:
            for itm in items[:2]:
                title = sanitize_text(itm.get("title", "Action Item"))
                desc = sanitize_text(itm.get("description", ""))
                action = sanitize_text(itm.get("action", ""))
                
                page3.draw_rect(fitz.Rect(margin_left, y3, margin_right, y3 + 36), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.6)
                page3.insert_text((margin_left + 8, y3 + 12), f"-> {title}", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
                page3.insert_textbox(fitz.Rect(margin_left + 8, y3 + 14, margin_right - 8, y3 + 34), f"{desc} Recommended: {action}", fontsize=7.5, color=COLOR_TEXT_MUTED)
                y3 += 40
        else:
            page3.insert_text((margin_left + 10, y3 + 10), "No specific action items generated for this tier.", fontsize=7.5, color=COLOR_TEXT_MUTED)
            y3 += 18
        y3 += 6

    # Topics to Revise Box
    y3 += 6
    page3.insert_text((margin_left, y3), "TARGETED CONCEPTS TO REVISE", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page3.draw_line(fitz.Point(margin_left, y3 + 4), fitz.Point(margin_right, y3 + 4), color=COLOR_CYAN, width=1.5)
    y3 += 16

    page3.draw_rect(fitz.Rect(margin_left, y3, margin_right, y3 + 55), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    topics = combined_summary.get("topics_to_revise", ["Core architectural patterns and internal mechanics."])
    top_str = " | ".join(sanitize_text(t) for t in topics[:6])
    page3.insert_textbox(fitz.Rect(margin_left + 10, y3 + 10, margin_right - 10, y3 + 48), f"Key Focus Items: {top_str}", fontsize=8, color=COLOR_TEXT)

    # Footer Page 3
    page3.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page3.insert_text((margin_left, height - 22), "InterviewSense AI -- Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)

    # =========================================================================
    # PAGE 4+: QUESTION-BY-QUESTION DETAILED EVALUATION
    # =========================================================================
    page_q = doc.new_page(width=width, height=height)

    # Top Header Banner
    page_q.draw_rect(fitz.Rect(0, 0, width, 55), color=None, fill=COLOR_PRIMARY)
    page_q.insert_text((margin_left, 32), "QUESTION-BY-QUESTION DETAILED EVALUATION", fontsize=12, color=COLOR_CYAN, fontname="helv")
    page_q.insert_text((margin_left, 46), "Detailed Rubrics, Submitted Responses, and Expert Model Answers", fontsize=8.5, color=COLOR_WHITE, fontname="helv")

    yq = 75

    for idx, e in enumerate(evals):
        q_num = e.get("question_number", idx + 1)
        q_score = e.get("score", 0)
        q_skill = sanitize_text(e.get("skill", "General"))
        q_diff = sanitize_text(e.get("difficulty", "Intermediate"))
        q_text = sanitize_text(e.get("question", ""))
        q_ans = sanitize_text(e.get("candidate_answer", ""))
        q_suggested = sanitize_text(e.get("suggested_answer", ""))
        q_well = [sanitize_text(w) for w in e.get("what_you_did_well", [])]
        q_miss = [sanitize_text(m) for m in e.get("missing_points", [])]

        # Multi-modal badges
        q_v = q_vis_results.get(idx, {})
        q_a = audio_results.get(idx, {})
        v_vis = q_v.get("face_visibility_pct", 0.0)
        v_cam = q_v.get("gaze_summary", {}).get("approx_camera_facing_pct", 0.0)
        a_wpm = q_a.get("words_per_minute", 0.0)
        a_fil = q_a.get("filler_words", 0)

        card_height = 160
        # Check if card fits on current page
        if yq + card_height > height - 45:
            # Footer on completed question page
            page_q.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
            page_q.insert_text((margin_left, height - 22), "InterviewSense AI -- Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)
            
            page_q = doc.new_page(width=width, height=height)
            page_q.draw_rect(fitz.Rect(0, 0, width, 40), color=None, fill=COLOR_PRIMARY)
            page_q.insert_text((margin_left, 26), "QUESTION-BY-QUESTION DETAILED EVALUATION (CONTINUED)", fontsize=11, color=COLOR_CYAN, fontname="helv")
            yq = 55

        # Card Container
        page_q.draw_rect(fitz.Rect(margin_left, yq, margin_right, yq + card_height), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
        
        # Header inside Question Card
        page_q.draw_rect(fitz.Rect(margin_left, yq, margin_right, yq + 22), color=None, fill=COLOR_GRAY_LIGHT)
        page_q.insert_text((margin_left + 8, yq + 15), f"Question {q_num} | {q_skill} ({q_diff})", fontsize=8.5, color=COLOR_PRIMARY, fontname="helv")
        
        score_tag = f"Score: {q_score}/100"
        score_c = COLOR_GREEN if q_score >= 70 else COLOR_ORANGE if q_score >= 40 else COLOR_RED
        page_q.insert_text((margin_right - 80, yq + 15), score_tag, fontsize=8.5, color=score_c, fontname="helv")

        # Multi-modal telemetry row
        page_q.insert_text((margin_left + 8, yq + 32), f"Spoken: {a_wpm} WPM ({a_fil} fillers)  |  Webcam: {v_vis}% visible, {v_cam}% camera-facing", fontsize=7, color=COLOR_CYAN, fontname="helv")

        # Question Prompt
        page_q.insert_textbox(fitz.Rect(margin_left + 8, yq + 36, margin_right - 8, yq + 58), f"Prompt: {q_text}", fontsize=8, color=COLOR_PRIMARY)

        # Candidate Answer Snippet
        ans_disp = truncate_text(q_ans, 200) if q_ans else "[No answer submitted - Unanswered]"
        ans_color = COLOR_TEXT if q_ans else COLOR_RED
        page_q.insert_textbox(fitz.Rect(margin_left + 8, yq + 58, margin_right - 8, yq + 84), f"Candidate Answer: {ans_disp}", fontsize=7.5, color=ans_color)

        # What went well & Missing points
        w_text = f"Strengths: {', '.join(q_well[:2])}" if q_well else "Strengths: Attempted response"
        m_text = f"Key Focus: {', '.join(q_miss[:2])}" if q_miss else "Key Focus: None"
        page_q.insert_textbox(fitz.Rect(margin_left + 8, yq + 86, margin_right - 8, yq + 104), truncate_text(w_text, 140), fontsize=7.5, color=(0.1, 0.6, 0.3))
        page_q.insert_textbox(fitz.Rect(margin_left + 8, yq + 104, margin_right - 8, yq + 122), truncate_text(m_text, 140), fontsize=7.5, color=(0.85, 0.45, 0.1))

        # Model Answer snippet
        page_q.insert_textbox(fitz.Rect(margin_left + 8, yq + 124, margin_right - 8, yq + 156), f"Model Answer: {truncate_text(q_suggested, 180)}", fontsize=7.5, color=COLOR_TEXT_MUTED)

        yq += card_height + 12

    # Footer on last question page
    page_q.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page_q.insert_text((margin_left, height - 22), "InterviewSense AI -- Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)

    # Stamp Two-Pass Page Numbers across all pages (Page X of Y)
    total_pages = doc.page_count
    for p_num in range(total_pages):
        p = doc[p_num]
        p.insert_text(
            (margin_right - 70, height - 22),
            f"Page {p_num + 1} of {total_pages}",
            fontsize=8,
            color=COLOR_TEXT_MUTED,
            fontname="helv"
        )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
