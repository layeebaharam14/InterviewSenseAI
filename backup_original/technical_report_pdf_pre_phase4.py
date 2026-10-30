"""
technical_report_pdf.py
PDF Report Generation Module for InterviewSense AI Technical Interview Results.
Generates comprehensive, multi-page, formatted PDF reports using PyMuPDF (fitz).
Includes:
- Technical Answer Evaluation & Rubric Criteria
- Speech and Audio Delivery Insights
- Advanced Facial, Eye-Gaze and Posture Analysis
- Transparent webcam limitations and disclaimers
"""

import io
from datetime import datetime
from typing import Dict, Any, List
import pymupdf as fitz

def truncate_text(text: str, max_chars: int = 400) -> str:
    """Safely truncates long text blocks for PDF display."""
    if not text:
        return ""
    text = str(text).strip()
    if len(text) > max_chars:
        return text[:max_chars - 3] + "..."
    return text

def generate_technical_pdf_report(session_summary: Dict[str, Any], evaluation_results: Dict[str, Any]) -> bytes:
    """
    Generates a structured PDF performance report for a Technical Interview session.

    Parameters:
        session_summary: Metadata dict with domain, skills, difficulty, total_questions, visual_analysis, etc.
        evaluation_results: Results dict from technical_evaluation.evaluate_technical_interview.

    Returns:
        bytes: Binary PDF content.
    """
    doc = fitz.open()
    width, height = 595, 842  # A4 Dimensions in points
    margin_left = 40
    margin_right = 555
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

    # -------------------------------------------------------------------------
    # PAGE 1: EXECUTIVE TECHNICAL PERFORMANCE SUMMARY
    # -------------------------------------------------------------------------
    page1 = doc.new_page(width=width, height=height)

    # Top Header Banner
    page1.draw_rect(fitz.Rect(0, 0, width, 75), color=None, fill=COLOR_PRIMARY)
    page1.insert_text((margin_left, 36), "INTERVIEWSENSE AI", fontsize=16, color=COLOR_CYAN, fontname="helv", render_mode=0)
    page1.insert_text((margin_left, 56), "Technical Interview Performance Evaluation Report", fontsize=11, color=COLOR_WHITE, fontname="helv")
    
    timestamp = session_summary.get("timestamp", datetime.now().strftime("%B %d, %Y - %I:%M %p"))
    page1.insert_text((width - 200, 48), timestamp, fontsize=8, color=(0.7, 0.8, 0.9), fontname="helv")

    y = 95

    # Overall Score Box
    score_box_height = 80
    page1.draw_rect(fitz.Rect(margin_left, y, margin_right, y + score_box_height), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=1)
    
    page1.insert_text((margin_left + 20, y + 25), "OVERALL TECHNICAL SCORE", fontsize=10, color=COLOR_TEXT_MUTED, fontname="helv")
    page1.insert_text((margin_left + 20, y + 62), f"{overall_sc}", fontsize=36, color=COLOR_PRIMARY, fontname="helv")
    page1.insert_text((margin_left + 80, y + 55), "/ 100", fontsize=14, color=COLOR_TEXT_MUTED, fontname="helv")

    # Classification Badge
    page1.draw_rect(fitz.Rect(margin_left + 150, y + 22, margin_left + 330, y + 55), color=None, fill=COLOR_PRIMARY)
    page1.insert_text((margin_left + 165, y + 43), f"Level: {perf_level}", fontsize=12, color=perf_color, fontname="helv")

    # Right Column Summary in Score Box
    domain_text = str(session_summary.get("domain", "General"))[:30]
    page1.insert_text((margin_left + 355, y + 25), f"Domain: {domain_text}", fontsize=9, color=COLOR_TEXT, fontname="helv")
    page1.insert_text((margin_left + 355, y + 42), f"Difficulty: {session_summary.get('difficulty', 'Intermediate')}", fontsize=9, color=COLOR_TEXT, fontname="helv")
    page1.insert_text((margin_left + 355, y + 59), f"Questions: {evaluation_results.get('answered_questions', 0)} Answered / {evaluation_results.get('total_questions', 0)} Total", fontsize=9, color=COLOR_TEXT, fontname="helv")

    y += score_box_height + 25

    # Section 1: Evaluation Criteria Scores
    page1.insert_text((margin_left, y), "EVALUATION CRITERIA BREAKDOWN", fontsize=11, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 18

    # Calculate criteria averages
    evals = evaluation_results.get("evaluations", [])
    tot_evals = max(len(evals), 1)
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
        page1.insert_text((box_x + 8, y + 36), c_score, fontsize=9.5, color=COLOR_PRIMARY, fontname="helv")
        page1.insert_text((box_x + col_w - 36, y + 36), c_pct, fontsize=8, color=COLOR_CYAN, fontname="helv")

    y += 66

    # Section 2: Skill-wise Performance Breakdown
    page1.insert_text((margin_left, y), "SKILL-WISE PERFORMANCE BREAKDOWN", fontsize=11, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 18

    skill_avgs = evaluation_results.get("skill_averages", {})
    if skill_avgs:
        for sk_name, sk_score in list(skill_avgs.items())[:4]:
            sk_level = "Excellent" if sk_score >= 90 else "Very Good" if sk_score >= 75 else "Good" if sk_score >= 60 else "Needs Improvement" if sk_score >= 40 else "Poor"
            page1.insert_text((margin_left + 10, y + 10), sk_name[:40], fontsize=9, color=COLOR_TEXT, fontname="helv")
            page1.insert_text((margin_left + 320, y + 10), f"Avg Score: {sk_score}/100", fontsize=9, color=COLOR_PRIMARY, fontname="helv")
            page1.insert_text((margin_left + 440, y + 10), f"Level: {sk_level}", fontsize=9, color=COLOR_TEXT_MUTED, fontname="helv")
            
            bar_y = y + 14
            page1.draw_line(fitz.Point(margin_left + 10, bar_y), fitz.Point(margin_left + 500, bar_y), color=(0.9, 0.92, 0.95), width=3)
            fill_width = margin_left + 10 + (490 * (min(100.0, sk_score) / 100.0))
            page1.draw_line(fitz.Point(margin_left + 10, bar_y), fitz.Point(fill_width, bar_y), color=COLOR_CYAN, width=3)
            y += 24
    else:
        page1.insert_text((margin_left + 10, y + 12), "No skill data evaluated.", fontsize=9, color=COLOR_TEXT_MUTED)
        y += 20

    y += 15

    # Section 3: Strengths and Focus Areas
    col_width_half = (usable_width - 15) / 2
    
    # Left Box: Strengths
    page1.draw_rect(fitz.Rect(margin_left, y, margin_left + col_width_half, y + 125), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page1.insert_text((margin_left + 10, y + 18), "KEY TECHNICAL STRENGTHS", fontsize=9.5, color=(0.1, 0.6, 0.3), fontname="helv")
    
    strengths = []
    for e in evals:
        if e.get("score", 0) >= 60:
            for w in e.get("what_you_did_well", []):
                if w not in strengths:
                    strengths.append(w)
    if not strengths:
        strengths = ["Demonstrated effort in addressing technical questions across the chosen domain."]

    s_y = y + 36
    for st_item in strengths[:3]:
        page1.insert_textbox(fitz.Rect(margin_left + 10, s_y, margin_left + col_width_half - 10, s_y + 26), f"• {st_item}", fontsize=8, color=COLOR_TEXT)
        s_y += 28

    # Right Box: Areas to Improve
    right_x = margin_left + col_width_half + 15
    page1.draw_rect(fitz.Rect(right_x, y, margin_right, y + 125), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page1.insert_text((right_x + 10, y + 18), "AREAS REQUIRING IMPROVEMENT", fontsize=9.5, color=(0.85, 0.45, 0.1), fontname="helv")

    improvements = []
    for e in evals:
        for imp in e.get("areas_to_improve", []):
            if imp not in improvements:
                improvements.append(imp)
    if not improvements:
        improvements = ["Focus on writing complete syntax snippets and exploring architectural edge cases."]

    i_y = y + 36
    for imp_item in improvements[:3]:
        page1.insert_textbox(fitz.Rect(right_x + 10, i_y, margin_right - 10, i_y + 26), f"• {imp_item}", fontsize=8, color=COLOR_TEXT)
        i_y += 28

    y += 140

    # Section 4: Recommended Next Steps
    page1.insert_text((margin_left, y), "RECOMMENDED NEXT STEPS", fontsize=11, color=COLOR_PRIMARY, fontname="helv")
    page1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 18

    weakest_skill = evaluation_results.get("weakest_skill", "Core Technical Topics")
    recs = [
        f"Targeted Revision: Conduct focused review on {weakest_skill} to clarify core mechanisms.",
        "Complexity & Memory: Explain Big-O runtime complexity and memory trade-offs consistently.",
        "Code Synthesis: Integrate syntactic keywords and edge-case exceptions in oral explanations."
    ]
    for r_text in recs:
        page1.insert_textbox(fitz.Rect(margin_left + 10, y, margin_right - 10, y + 18), f"→ {r_text}", fontsize=8.5, color=COLOR_TEXT)
        y += 20

    # Footer Page 1
    page1.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page1.insert_text((margin_left, height - 22), "InterviewSense AI — Automated Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)
    page1.insert_text((margin_right - 55, height - 22), "Page 1", fontsize=8, color=COLOR_TEXT_MUTED)

    # -------------------------------------------------------------------------
    # PAGE 2: FACIAL, EYE-GAZE AND POSTURE BEHAVIOURAL ANALYSIS
    # -------------------------------------------------------------------------
    page_vis = doc.new_page(width=width, height=height)

    # Top Header Banner
    page_vis.draw_rect(fitz.Rect(0, 0, width, 55), color=None, fill=COLOR_PRIMARY)
    page_vis.insert_text((margin_left, 32), "FACIAL, EYE-GAZE AND POSTURE BEHAVIOURAL ANALYSIS", fontsize=12, color=COLOR_CYAN, fontname="helv")
    page_vis.insert_text((margin_left, 46), "Automated Landmark-Based Visual Engagement & Pacing Insights", fontsize=9, color=COLOR_WHITE, fontname="helv")

    y_v = 75

    vis_summary = session_summary.get("visual_analysis", {})
    face_vis_pct = vis_summary.get("overall_face_visibility_pct", 0.0)
    cam_facing_pct = vis_summary.get("overall_camera_facing_pct", 0.0)
    centering_pct = vis_summary.get("overall_face_centering_pct", 0.0)
    movement_str = vis_summary.get("overall_head_movement", "Natural")
    posture_str = vis_summary.get("dominant_posture", "Upright")

    # Metrics Summary Grid
    page_vis.insert_text((margin_left, y_v), "OVERALL VISUAL ENGAGEMENT METRICS", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page_vis.draw_line(fitz.Point(margin_left, y_v + 4), fitz.Point(margin_right, y_v + 4), color=COLOR_CYAN, width=1.5)
    y_v += 18

    vis_metrics_cards = [
        ("Face Visibility", f"{face_vis_pct}%", "In camera frame"),
        ("Camera-Facing", f"{cam_facing_pct}%", "Approx. eye gaze"),
        ("Face-Centering", f"{centering_pct}%", "In central zone"),
        ("Head Movement", str(movement_str)[:15], "Pacing / stability"),
        ("Posture", str(posture_str)[:15], "Upper-body alignment")
    ]

    col_vm = usable_width / 5
    for idx, (m_title, m_val, m_sub) in enumerate(vis_metrics_cards):
        bx = margin_left + idx * col_vm
        page_vis.draw_rect(fitz.Rect(bx, y_v, bx + col_vm - 6, y_v + 52), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=0.8)
        page_vis.insert_textbox(fitz.Rect(bx + 4, y_v + 4, bx + col_vm - 10, y_v + 20), m_title, fontsize=7.5, color=COLOR_TEXT_MUTED, align=1)
        page_vis.insert_textbox(fitz.Rect(bx + 4, y_v + 22, bx + col_vm - 10, y_v + 38), m_val, fontsize=10, color=COLOR_PRIMARY, align=1)
        page_vis.insert_textbox(fitz.Rect(bx + 4, y_v + 38, bx + col_vm - 10, y_v + 50), m_sub, fontsize=6.5, color=COLOR_CYAN, align=1)

    y_v += 70

    # Observations & Posture Insights
    col_w_v2 = (usable_width - 15) / 2

    # Left Box: Key Visual Observations
    page_vis.draw_rect(fitz.Rect(margin_left, y_v, margin_left + col_w_v2, y_v + 130), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page_vis.insert_text((margin_left + 10, y_v + 18), "KEY VISUAL OBSERVATIONS", fontsize=9.5, color=COLOR_PRIMARY, fontname="helv")
    
    obs_list = vis_summary.get("key_observations", [])
    if not obs_list:
        obs_list = ["Maintained consistent webcam engagement during technical responses."]
    
    o_y = y_v + 36
    for obs in obs_list[:4]:
        page_vis.insert_textbox(fitz.Rect(margin_left + 10, o_y, margin_left + col_w_v2 - 10, o_y + 26), f"• {obs}", fontsize=8, color=COLOR_TEXT)
        o_y += 24

    # Right Box: Behavioral & Framing Suggestions
    right_vx = margin_left + col_w_v2 + 15
    page_vis.draw_rect(fitz.Rect(right_vx, y_v, margin_right, y_v + 130), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page_vis.insert_text((right_vx + 10, y_v + 18), "FRAMING & ENGAGEMENT SUGGESTIONS", fontsize=9.5, color=COLOR_CYAN, fontname="helv")
    
    sugg_list = vis_summary.get("improvement_suggestions", [])
    if not sugg_list:
        sugg_list = ["Keep your face centered and well-illuminated throughout the interview."]

    s_vy = y_v + 36
    for sg in sugg_list[:4]:
        page_vis.insert_textbox(fitz.Rect(right_vx + 10, s_vy, margin_right - 10, s_vy + 26), f"• {sg}", fontsize=8, color=COLOR_TEXT)
        s_vy += 24

    y_v += 145

    # Section: Question-wise Visual Engagement Summary Table
    page_vis.insert_text((margin_left, y_v), "QUESTION-WISE VISUAL ENGAGEMENT BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    page_vis.draw_line(fitz.Point(margin_left, y_v + 4), fitz.Point(margin_right, y_v + 4), color=COLOR_CYAN, width=1.5)
    y_v += 18

    # Table Header
    page_vis.draw_rect(fitz.Rect(margin_left, y_v, margin_right, y_v + 20), color=None, fill=COLOR_GRAY_LIGHT)
    page_vis.insert_text((margin_left + 8, y_v + 14), "Q#", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    page_vis.insert_text((margin_left + 35, y_v + 14), "Topic / Skill", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    page_vis.insert_text((margin_left + 175, y_v + 14), "Visibility %", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    page_vis.insert_text((margin_left + 260, y_v + 14), "Camera-Facing %", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    page_vis.insert_text((margin_left + 370, y_v + 14), "Movement Level", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    page_vis.insert_text((margin_left + 475, y_v + 14), "Status", fontsize=8, color=COLOR_PRIMARY, fontname="helv")
    y_v += 24

    q_vis_results = session_summary.get("question_visual_results", {})
    for q_i in range(session_summary.get("total_questions", 0)):
        q_v = q_vis_results.get(q_i, {})
        v_skill = str(q_v.get("skill", "General"))[:22]
        v_vis = f"{q_v.get('face_visibility_pct', 0.0)}%"
        v_cam = f"{q_v.get('gaze_summary', {}).get('approx_camera_facing_pct', 0.0)}%"
        v_mov = str(q_v.get("head_pose_summary", {}).get("movement_level", "Natural"))[:18]
        v_stat = str(q_v.get("visual_analysis_status", "Completed")).capitalize()

        bg_row = COLOR_WHITE if q_i % 2 == 0 else COLOR_GRAY_LIGHT
        page_vis.draw_rect(fitz.Rect(margin_left, y_v, margin_right, y_v + 18), color=None, fill=bg_row)
        page_vis.insert_text((margin_left + 8, y_v + 13), f"Q{q_i + 1}", fontsize=7.5, color=COLOR_TEXT, fontname="helv")
        page_vis.insert_text((margin_left + 35, y_v + 13), v_skill, fontsize=7.5, color=COLOR_TEXT, fontname="helv")
        page_vis.insert_text((margin_left + 185, y_v + 13), v_vis, fontsize=7.5, color=COLOR_PRIMARY, fontname="helv")
        page_vis.insert_text((margin_left + 275, y_v + 13), v_cam, fontsize=7.5, color=COLOR_CYAN, fontname="helv")
        page_vis.insert_text((margin_left + 370, y_v + 13), v_mov, fontsize=7.5, color=COLOR_TEXT, fontname="helv")
        page_vis.insert_text((margin_left + 475, y_v + 13), v_stat, fontsize=7.5, color=COLOR_GREEN if v_stat == "Completed" else COLOR_ORANGE, fontname="helv")
        y_v += 20

    y_v += 15

    # Limitations & Pseudoscience Disclaimer Box
    page_vis.draw_rect(fitz.Rect(margin_left, y_v, margin_right, y_v + 62), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
    page_vis.insert_text((margin_left + 10, y_v + 16), "IMPORTANT TRANSPARENCY DISCLAIMER & LIMITATIONS", fontsize=8.5, color=COLOR_TEXT_MUTED, fontname="helv")
    disclaimer_text = (
        "Webcam-based gaze, head-pose, and posture evaluations are geometric landmark estimations reflecting camera framing "
        "and physical orientation. InterviewSense AI strictly avoids inferring personality, honesty, intelligence, cognitive ability, "
        "or emotional state from video recordings. Visual metrics do NOT alter or influence technical correctness scores."
    )
    page_vis.insert_textbox(fitz.Rect(margin_left + 10, y_v + 22, margin_right - 10, y_v + 58), disclaimer_text, fontsize=7.5, color=COLOR_TEXT_MUTED)

    # Footer Page 2
    page_vis.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page_vis.insert_text((margin_left, height - 22), "InterviewSense AI — Automated Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)
    page_vis.insert_text((margin_right - 55, height - 22), "Page 2", fontsize=8, color=COLOR_TEXT_MUTED)

    # -------------------------------------------------------------------------
    # PAGE 3+: QUESTION-BY-QUESTION DETAILED EVALUATION
    # -------------------------------------------------------------------------
    page2 = doc.new_page(width=width, height=height)

    # Top Header Banner
    page2.draw_rect(fitz.Rect(0, 0, width, 55), color=None, fill=COLOR_PRIMARY)
    page2.insert_text((margin_left, 32), "QUESTION-BY-QUESTION DETAILED EVALUATION", fontsize=12, color=COLOR_CYAN, fontname="helv")
    page2.insert_text((margin_left, 46), "Comprehensive Breakdown of Submitted Answers, Rubrics, and Model Answers", fontsize=9, color=COLOR_WHITE, fontname="helv")

    y2 = 75

    for idx, e in enumerate(evals):
        q_num = e.get("question_id", idx + 1)
        q_score = e.get("score", 0)
        q_skill = e.get("skill", "General")
        q_diff = e.get("difficulty", "Intermediate")
        q_text = e.get("question", "")
        q_ans = e.get("candidate_answer", "")
        q_suggested = e.get("suggested_answer", "")
        q_well = e.get("what_you_did_well", [])
        q_miss = e.get("missing_points", [])

        # Check if we need another page
        if y2 + 155 > height - 40:
            page2.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
            page2.insert_text((margin_left, height - 22), "InterviewSense AI — Automated Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)
            page2.insert_text((margin_right - 55, height - 22), f"Page {doc.page_count}", fontsize=8, color=COLOR_TEXT_MUTED)
            
            page2 = doc.new_page(width=width, height=height)
            page2.draw_rect(fitz.Rect(0, 0, width, 40), color=None, fill=COLOR_PRIMARY)
            page2.insert_text((margin_left, 26), "QUESTION-BY-QUESTION DETAILED EVALUATION (CONTINUED)", fontsize=11, color=COLOR_CYAN, fontname="helv")
            y2 = 60

        card_height = 145
        page2.draw_rect(fitz.Rect(margin_left, y2, margin_right, y2 + card_height), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
        
        # Header inside Question Card
        page2.draw_rect(fitz.Rect(margin_left, y2, margin_right, y2 + 24), color=None, fill=COLOR_GRAY_LIGHT)
        page2.insert_text((margin_left + 10, y2 + 16), f"Question {q_num} | {q_skill} ({q_diff})", fontsize=9, color=COLOR_PRIMARY, fontname="helv")
        
        score_tag = f"Score: {q_score}/100"
        page2.insert_text((margin_right - 90, y2 + 16), score_tag, fontsize=9, color=COLOR_CYAN if q_score >= 70 else COLOR_ORANGE if q_score >= 40 else COLOR_RED, fontname="helv")

        # Question Prompt
        page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 28, margin_right - 10, y2 + 50), f"Q: {q_text}", fontsize=8.5, color=COLOR_PRIMARY)

        # Candidate Answer Snippet
        ans_display = truncate_text(q_ans, 180) if q_ans else "[No answer submitted - Unanswered]"
        page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 52, margin_right - 10, y2 + 78), f"Candidate Answer: {ans_display}", fontsize=8, color=COLOR_TEXT_MUTED)

        # What went well & Missing points
        w_text = f"Well: {', '.join(q_well[:2])}" if q_well else "Well: Attempted"
        m_text = f"Missing: {', '.join(q_miss[:2])}" if q_miss else "Missing: None"
        page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 80, margin_right - 10, y2 + 98), truncate_text(w_text, 120), fontsize=7.5, color=(0.1, 0.6, 0.3))
        page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 98, margin_right - 10, y2 + 116), truncate_text(m_text, 120), fontsize=7.5, color=(0.85, 0.45, 0.1))

        # Model Answer snippet
        page2.insert_textbox(fitz.Rect(margin_left + 10, y2 + 118, margin_right - 10, y2 + 140), f"Model Answer: {truncate_text(q_suggested, 140)}", fontsize=7.5, color=COLOR_TEXT)

        y2 += card_height + 15

    # Footer Last Page
    page2.draw_line(fitz.Point(margin_left, height - 35), fitz.Point(margin_right, height - 35), color=COLOR_BORDER, width=0.5)
    page2.insert_text((margin_left, height - 22), "InterviewSense AI — Automated Technical Interview System", fontsize=8, color=COLOR_TEXT_MUTED)
    page2.insert_text((margin_right - 55, height - 22), f"Page {doc.page_count} of {doc.page_count}", fontsize=8, color=COLOR_TEXT_MUTED)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
