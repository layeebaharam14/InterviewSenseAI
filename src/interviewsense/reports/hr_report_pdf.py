"""
hr_report_pdf.py — InterviewSense AI
Comprehensive Multi-Page PDF Report Generation for Mock HR Interview.
Generates structured, professional behavioral and speech performance reports using PyMuPDF (fitz).
"""

import io
import re
from datetime import datetime
from typing import Dict, Any, List
import pymupdf as fitz

from src.interviewsense.core.insights import generate_mock_interview_summary


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
    return "".join(c if ord(c) < 256 else " " for c in text)


def truncate_text(text: str, max_chars: int = 400) -> str:
    """Safely truncates long text blocks for PDF display."""
    if not text:
        return ""
    text = sanitize_text(text)
    if len(text) > max_chars:
        return text[:max_chars - 3] + "..."
    return text


def generate_hr_pdf_report(session_summary: Dict[str, Any], evaluation_results: Dict[str, Any] = None) -> bytes:
    """
    Generates a structured, professional multi-page PDF performance report for a Mock HR Interview session.

    Parameters:
        session_summary: Dict from generate_mock_interview_summary(...) or session metadata.
        evaluation_results: Optional supplementary results dict (merged if provided).

    Returns:
        bytes: Binary PDF content.
    """
    # Merge if separate evaluation_results provided
    summary = dict(session_summary)
    if evaluation_results and isinstance(evaluation_results, dict):
        for k, v in evaluation_results.items():
            if k not in summary or summary[k] is None:
                summary[k] = v

    doc = fitz.open()
    width, height = 595, 842  # A4 Dimensions
    margin_left = 36
    margin_right = 559
    usable_width = margin_right - margin_left

    # Color Palette (RGB normalized 0.0 - 1.0)
    COLOR_PRIMARY = (0.04, 0.07, 0.13)      # Dark Navy #0b1120
    COLOR_CYAN = (0.22, 0.74, 0.97)         # Cyan #38bdf8
    COLOR_WHITE = (1.0, 1.0, 1.0)           # White
    COLOR_GRAY_LIGHT = (0.94, 0.96, 0.98)   # Light Gray Background
    COLOR_BORDER = (0.8, 0.85, 0.9)         # Border Gray
    COLOR_TEXT = (0.1, 0.15, 0.2)           # Main text
    COLOR_TEXT_MUTED = (0.4, 0.45, 0.55)    # Muted text
    COLOR_GREEN = (0.13, 0.77, 0.37)        # Emerald
    COLOR_AMBER = (0.98, 0.76, 0.08)        # Amber
    COLOR_ORANGE = (0.98, 0.57, 0.23)       # Orange
    COLOR_RED = (0.94, 0.27, 0.27)          # Red

    candidate_name = sanitize_text(summary.get("candidate_name") or "Candidate")
    timestamp = sanitize_text(summary.get("timestamp") or datetime.now().strftime("%B %d, %Y - %I:%M %p"))
    overall_score = summary.get("overall_score", 0)
    verdict = sanitize_text(summary.get("verdict", "Needs Improvement"))
    total_q = summary.get("total_questions", 0)
    audio_q = summary.get("audio_questions_evaluated", 0)
    video_q = summary.get("video_questions_evaluated", 0)
    coverage_status = sanitize_text(summary.get("coverage_status", "Evaluation Complete"))
    score_note = sanitize_text(summary.get("score_note", ""))

    conf_score = summary.get("confidence_score", 0)
    nerv_score = summary.get("nervousness_score", 0)
    comm_score = summary.get("communication_score")

    # Verdict color
    if "Ready" in verdict and "Not" not in verdict:
        verdict_color = COLOR_GREEN
    elif "Improvement" in verdict:
        verdict_color = COLOR_AMBER
    else:
        verdict_color = COLOR_RED

    # =========================================================================
    # PAGE 1: COVER, EXECUTIVE SCORE & PERFORMANCE BREAKDOWN
    # =========================================================================
    p1 = doc.new_page(width=width, height=height)

    # Top Header Banner
    p1.draw_rect(fitz.Rect(0, 0, width, 80), color=None, fill=COLOR_PRIMARY)
    p1.insert_text((margin_left, 32), "INTERVIEWSENSE AI", fontsize=15, color=COLOR_CYAN, fontname="helv")
    p1.insert_text((margin_left, 52), "Mock Interview Performance & Behavioral Analytics Report", fontsize=11, color=COLOR_WHITE, fontname="helv")
    p1.insert_text((margin_left, 68), f"Candidate: {candidate_name}  |  Session Date: {timestamp}", fontsize=8.5, color=(0.7, 0.8, 0.9), fontname="helv")
    p1.insert_text((width - 150, 48), "STATUS: COMPLETED", fontsize=9, color=COLOR_GREEN, fontname="helv")

    y = 96

    # Overall Score Box
    score_box_h = 84
    p1.draw_rect(fitz.Rect(margin_left, y, margin_right, y + score_box_h), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=1)
    p1.insert_text((margin_left + 16, y + 24), "OVERALL SIMULATION SCORE", fontsize=9, color=COLOR_TEXT_MUTED, fontname="helv")
    p1.insert_text((margin_left + 16, y + 64), f"{overall_score}", fontsize=36, color=COLOR_PRIMARY, fontname="helv")
    p1.insert_text((margin_left + 72, y + 56), "/ 100", fontsize=13, color=COLOR_TEXT_MUTED, fontname="helv")

    # Final Verdict Badge
    verdict_badge_w = 175
    p1.draw_rect(fitz.Rect(margin_left + 140, y + 22, margin_left + 140 + verdict_badge_w, y + 56), color=None, fill=COLOR_PRIMARY)
    p1.insert_text((margin_left + 152, y + 43), f"Verdict: {verdict}", fontsize=11, color=verdict_color, fontname="helv")

    # Right info in Score Box
    p1.insert_text((margin_left + 335, y + 24), f"Questions Completed: {total_q}", fontsize=8.5, color=COLOR_TEXT, fontname="helv")
    p1.insert_text((margin_left + 335, y + 42), f"Coverage: {truncate_text(coverage_status, 32)}", fontsize=8.5, color=COLOR_TEXT, fontname="helv")
    if score_note:
        p1.insert_text((margin_left + 335, y + 60), f"Note: {truncate_text(score_note, 34)}", fontsize=8, color=COLOR_ORANGE, fontname="helv")
    else:
        p1.insert_text((margin_left + 335, y + 60), "Mode: Behavioral & Speech Simulation", fontsize=8.5, color=COLOR_TEXT_MUTED, fontname="helv")

    y += score_box_h + 18

    # Performance Metrics Breakdown Section
    p1.insert_text((margin_left, y), "PERFORMANCE METRICS BREAKDOWN", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    p1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    conf_lvl = "High" if conf_score >= 80 else ("Moderate" if conf_score >= 55 else "Low")
    nerv_lvl = "Low" if nerv_score <= 25 else ("Moderate" if nerv_score <= 50 else "High")
    if comm_score is not None and audio_q > 0:
        comm_val = f"{comm_score} / 100"
        comm_lvl = "Good" if comm_score >= 75 else ("Moderate" if comm_score >= 50 else "Low")
    else:
        comm_val = "N/A"
        comm_lvl = "Audio Unavailable"

    audio_cov_pct = summary.get("audio_coverage_pct", 100.0)
    video_cov_pct = summary.get("video_coverage_pct", 100.0)

    metric_cards = [
        ("Confidence Score", f"{conf_score} / 100", conf_lvl, "Gaze & Face Presence"),
        ("Nervousness Index", f"{nerv_score} / 100", nerv_lvl, "Physical Composure"),
        ("Communication Score", comm_val, comm_lvl, "Fluency & Pacing"),
        ("Evaluation Coverage", f"{audio_q}/{total_q} Audio", f"{video_q}/{total_q} Video", "Telemetry Coverage")
    ]

    card_w = usable_width / 4
    for idx, (m_title, m_val, m_lvl, m_desc) in enumerate(metric_cards):
        cx = margin_left + idx * card_w
        p1.draw_rect(fitz.Rect(cx, y, cx + card_w - 6, y + 58), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
        p1.insert_text((cx + 8, y + 14), m_title, fontsize=8, color=COLOR_TEXT_MUTED, fontname="helv")
        p1.insert_text((cx + 8, y + 33), m_val, fontsize=12, color=COLOR_PRIMARY, fontname="helv")
        p1.insert_text((cx + 8, y + 48), f"{m_lvl} · {m_desc}", fontsize=6.8, color=COLOR_CYAN, fontname="helv")

    y += 74

    # Executive Strengths Section
    p1.insert_text((margin_left, y), "EXECUTIVE ASSESSMENT & OBSERVED STRENGTHS", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    p1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    strengths = summary.get("strengths", [])
    if not strengths:
        strengths = ["Completed simulated interview session with behavioral tracking."]

    for s_idx, s in enumerate(strengths[:4]):
        clean_s = sanitize_text(s)
        p1.draw_circle(fitz.Point(margin_left + 8, y + 6), 2.5, color=COLOR_GREEN, fill=COLOR_GREEN)
        p1.insert_textbox(fitz.Rect(margin_left + 16, y, margin_right - 8, y + 24), clean_s, fontsize=8.5, color=COLOR_TEXT)
        y += 20

    y += 10

    # Areas for Improvement Section
    p1.insert_text((margin_left, y), "PRIORITY AREAS FOR IMPROVEMENT", fontsize=10.5, color=COLOR_PRIMARY, fontname="helv")
    p1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_CYAN, width=1.5)
    y += 16

    improvements = summary.get("improvements", [])
    if not improvements:
        improvements = ["Continue refining behavioral presence using structured practice."]

    for i_idx, imp in enumerate(improvements[:4]):
        clean_imp = sanitize_text(imp)
        p1.draw_circle(fitz.Point(margin_left + 8, y + 6), 2.5, color=COLOR_AMBER, fill=COLOR_AMBER)
        p1.insert_textbox(fitz.Rect(margin_left + 16, y, margin_right - 8, y + 24), clean_imp, fontsize=8.5, color=COLOR_TEXT)
        y += 20

    # Critical Issues (if any)
    critical_issues = summary.get("critical_issues", [])
    if critical_issues:
        y += 10
        p1.insert_text((margin_left, y), "CRITICAL AREAS TO ADDRESS", fontsize=10.5, color=COLOR_RED, fontname="helv")
        p1.draw_line(fitz.Point(margin_left, y + 4), fitz.Point(margin_right, y + 4), color=COLOR_RED, width=1.5)
        y += 16
        for crit in critical_issues[:3]:
            clean_crit = sanitize_text(crit)
            p1.draw_circle(fitz.Point(margin_left + 8, y + 6), 2.5, color=COLOR_RED, fill=COLOR_RED)
            p1.insert_textbox(fitz.Rect(margin_left + 16, y, margin_right - 8, y + 24), clean_crit, fontsize=8.5, color=COLOR_RED)
            y += 20

    # Draw footer for Page 1
    p1.draw_line(fitz.Point(margin_left, height - 32), fitz.Point(margin_right, height - 32), color=COLOR_BORDER, width=0.5)
    p1.insert_text((margin_left, height - 20), "InterviewSense AI -- Mock Interview Behavioral & Speech Evaluation", fontsize=7.5, color=COLOR_TEXT_MUTED)

    # =========================================================================
    # PAGE 2+: QUESTION-BY-QUESTION BEHAVIORAL & SPEECH BREAKDOWN
    # =========================================================================
    question_evals = summary.get("question_evaluations", [])

    if question_evals:
        p_current = doc.new_page(width=width, height=height)
        p_current.draw_rect(fitz.Rect(0, 0, width, 40), color=None, fill=COLOR_PRIMARY)
        p_current.insert_text((margin_left, 25), "INTERVIEWSENSE AI -- QUESTION-BY-QUESTION BEHAVIORAL BREAKDOWN", fontsize=10, color=COLOR_CYAN, fontname="helv")
        yq = 55

        for q_idx, q_data in enumerate(question_evals):
            q_text = sanitize_text(q_data.get("question", f"Question {q_idx + 1}"))
            transcript = sanitize_text(q_data.get("transcript", "[No response available]"))
            a_status = q_data.get("audio_status", "unavailable")
            v_status = q_data.get("video_status", "unavailable")

            words = q_data.get("word_count", 0)
            wpm = q_data.get("words_per_minute", 0.0)
            rate = sanitize_text(q_data.get("speech_rate", "—"))
            fillers = q_data.get("filler_words", 0)
            pauses = q_data.get("pauses", 0)

            eye_contact = sanitize_text(q_data.get("eye_contact", "unavailable")).capitalize()
            movement = sanitize_text(q_data.get("movement", "unavailable")).capitalize()
            posture = sanitize_text(q_data.get("posture", "unavailable")).capitalize()

            well_bullets = [sanitize_text(w) for w in q_data.get("what_went_well", [])[:2]]
            improve_bullets = [sanitize_text(imp) for imp in q_data.get("what_to_improve", [])[:2]]

            # Estimate required card height dynamically based on transcript and bullets
            trans_lines = max(1, len(transcript) // 75 + 1)
            ans_box_h = max(28, trans_lines * 14 + 10)
            card_h = 75 + ans_box_h + (len(well_bullets) * 16) + (len(improve_bullets) * 16)

            # Check if card fits on current page
            if yq + card_h > height - 60:
                # Footer on current page
                p_current.draw_line(fitz.Point(margin_left, height - 32), fitz.Point(margin_right, height - 32), color=COLOR_BORDER, width=0.5)
                p_current.insert_text((margin_left, height - 20), "InterviewSense AI -- Mock Interview Behavioral & Speech Evaluation", fontsize=7.5, color=COLOR_TEXT_MUTED)
                # New page
                p_current = doc.new_page(width=width, height=height)
                p_current.draw_rect(fitz.Rect(0, 0, width, 40), color=None, fill=COLOR_PRIMARY)
                p_current.insert_text((margin_left, 25), "INTERVIEWSENSE AI -- QUESTION-BY-QUESTION BEHAVIORAL BREAKDOWN", fontsize=10, color=COLOR_CYAN, fontname="helv")
                yq = 55

            # Draw Question Card Box
            p_current.draw_rect(fitz.Rect(margin_left, yq, margin_right, yq + card_h), color=COLOR_BORDER, fill=COLOR_WHITE, width=0.8)
            p_current.draw_rect(fitz.Rect(margin_left, yq, margin_right, yq + 22), color=None, fill=COLOR_GRAY_LIGHT)

            # Header inside Card
            p_current.insert_text((margin_left + 10, yq + 15), f"Q{q_idx + 1}: {truncate_text(q_text, 80)}", fontsize=9, color=COLOR_PRIMARY, fontname="helv")

            # Telemetry line
            if a_status == "transcribed":
                speech_telemetry = f"Speech: {words} words | {wpm} WPM ({rate}) | {fillers} filler(s) | {pauses} pause(s)"
            elif a_status == "silent":
                speech_telemetry = "Speech: No speech detected (silence)"
            else:
                speech_telemetry = "Speech: Audio unavailable (mic/SR failure)"

            if v_status == "detected":
                camera_telemetry = f"Camera: Eye Contact {eye_contact} | Movement {movement} | Posture {posture}"
            else:
                camera_telemetry = "Camera: Face presence unavailable"

            p_current.insert_text((margin_left + 10, yq + 34), truncate_text(f"{speech_telemetry}   |   {camera_telemetry}", 110), fontsize=7.2, color=COLOR_TEXT_MUTED, fontname="helv")

            # Candidate Response Box
            ans_y = yq + 40
            p_current.draw_rect(fitz.Rect(margin_left + 10, ans_y, margin_right - 10, ans_y + ans_box_h), color=COLOR_BORDER, fill=(0.97, 0.98, 0.99), width=0.5)
            ans_prefix = 'Candidate Response: "' if a_status == "transcribed" else "Status: "
            ans_suffix = '"' if a_status == "transcribed" else ""
            ans_full = f"{ans_prefix}{transcript}{ans_suffix}"
            p_current.insert_textbox(fitz.Rect(margin_left + 14, ans_y + 4, margin_right - 14, ans_y + ans_box_h - 4), truncate_text(ans_full, 300), fontsize=7.5, color=COLOR_TEXT)

            # Bullet points: What Went Well
            curr_b_y = ans_y + ans_box_h + 8
            for w in well_bullets:
                p_current.insert_text((margin_left + 10, curr_b_y), f"[OK] What went well: {truncate_text(w, 100)}", fontsize=7.5, color=(0.1, 0.6, 0.3), fontname="helv")
                curr_b_y += 15

            # Bullet points: What to Improve
            for imp in improve_bullets:
                p_current.insert_text((margin_left + 10, curr_b_y), f"-> What to improve: {truncate_text(imp, 100)}", fontsize=7.5, color=(0.85, 0.45, 0.1), fontname="helv")
                curr_b_y += 15

            yq += card_h + 12

        # Methodology & Limitations Box at end of questions
        limit_h = 105
        if yq + limit_h > height - 60:
            # Footer on current page
            p_current.draw_line(fitz.Point(margin_left, height - 32), fitz.Point(margin_right, height - 32), color=COLOR_BORDER, width=0.5)
            p_current.insert_text((margin_left, height - 20), "InterviewSense AI -- Mock Interview Behavioral & Speech Evaluation", fontsize=7.5, color=COLOR_TEXT_MUTED)
            # New page
            p_current = doc.new_page(width=width, height=height)
            p_current.draw_rect(fitz.Rect(0, 0, width, 40), color=None, fill=COLOR_PRIMARY)
            p_current.insert_text((margin_left, 25), "INTERVIEWSENSE AI -- METHODOLOGY & SCIENTIFIC LIMITATIONS", fontsize=10, color=COLOR_CYAN, fontname="helv")
            yq = 55

        # Draw Methodology box
        p_current.insert_text((margin_left, yq + 10), "METHODOLOGY, DATA INTEGRITY & SCIENTIFIC LIMITATIONS", fontsize=9.5, color=COLOR_PRIMARY, fontname="helv")
        p_current.draw_line(fitz.Point(margin_left, yq + 14), fitz.Point(margin_right, yq + 14), color=COLOR_CYAN, width=1.2)
        yq += 20

        p_current.draw_rect(fitz.Rect(margin_left, yq, margin_right, yq + 75), color=COLOR_BORDER, fill=COLOR_GRAY_LIGHT, width=0.8)
        lim_texts = [
            "* Non-Hallucination Guarantee: All metrics reflect actual camera frames and speech transcripts.",
            "* Sensor Approximation: Facial framing, eye gaze, and speech rate approximate observable cues.",
            "* Scientific Disclaimer: This tool does not claim to diagnose psychology, intelligence, or emotional states.",
            "* Constructive Purpose: Metrics are designed as practice feedback for interview preparation only."
        ]
        for l_idx, lt in enumerate(lim_texts):
            p_current.insert_text((margin_left + 10, yq + 16 + (l_idx * 14)), lt, fontsize=7.2, color=COLOR_TEXT_MUTED, fontname="helv")

        # Footer on last question page
        p_current.draw_line(fitz.Point(margin_left, height - 32), fitz.Point(margin_right, height - 32), color=COLOR_BORDER, width=0.5)
        p_current.insert_text((margin_left, height - 20), "InterviewSense AI -- Mock Interview Behavioral & Speech Evaluation", fontsize=7.5, color=COLOR_TEXT_MUTED)

    # Stamp Two-Pass Page Numbers across all pages (Page X of Y)
    total_pages = doc.page_count
    for p_num in range(total_pages):
        p = doc[p_num]
        p.insert_text(
            (margin_right - 65, height - 20),
            f"Page {p_num + 1} of {total_pages}",
            fontsize=7.5,
            color=COLOR_TEXT_MUTED,
            fontname="helv"
        )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
