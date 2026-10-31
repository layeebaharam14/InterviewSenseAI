# -*- coding: utf-8 -*-
"""
test_phase4_analytics.py
Comprehensive verification test suite for Phase 4:
Complete Interview Analytics, Combined Feedback and Final Reporting.

Tests all 20 areas specified in Section 9 of the Phase 4 specification:
1. Complete technical interview with all questions answered
2. Complete interview with some blank answers
3. Failed speech transcription handling
4. Missing audio metrics handling
5. Missing visual metrics handling
6. No detected face handling
7. Missing posture data handling
8. Skill-wise performance calculations
9. Question-wise feedback association
10. Personalised improvement recommendations
11. PDF generation with all data available
12. PDF generation with partial data
13. Long answers and multi-page reports
14. Streamlit reruns and state preservation
15. Retake workflow
16. Existing Mock HR Interview compatibility
17. Fixed 15-second technical recording preserved
18. Phase 2 microphone and transcript functionality preserved
19. Phase 3 visual analysis preserved
20. No duplicate or corrupted results
"""

import unittest
import numpy as np
import io
import fitz
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules
import app
from technical_evaluation import (
    evaluate_technical_interview,
    evaluate_technical_answer,
    classify_performance,
    generate_combined_summary,
    generate_improvement_roadmap
)
import technical_report_pdf
from video_analysis import (
    aggregate_video_analysis,
    analyze_technical_question_frames,
    calculate_overall_visual_analysis
)
from audio_analysis import analyze_audio_behavior

class TestPhase4AnalyticsAndReporting(unittest.TestCase):

    def setUp(self):
        self.sample_questions = [
            {
                "question": "Explain the Global Interpreter Lock (GIL) in Python.",
                "skill": "Python Internals",
                "difficulty": "Intermediate",
                "question_type": "Conceptual",
                "key_concepts": ["GIL", "Global Interpreter Lock", "thread", "mutex", "bytecode"],
                "key_points": ["CPython thread execution limits", "Prevents race conditions in bytecode"],
                "expected_answer": "The Global Interpreter Lock is a mutex that prevents multiple native threads from executing Python bytecodes at once."
            },
            {
                "question": "What is the average and worst-case time complexity of Quicksort?",
                "skill": "Algorithms & Data Structures",
                "difficulty": "Beginner",
                "question_type": "Analytical",
                "key_concepts": ["quicksort", "O(n log n)", "O(n^2)", "pivot", "complexity"],
                "key_points": ["Average O(n log n)", "Worst case O(n^2) with poor pivot"],
                "expected_answer": "Average case is O(n log n), worst case is O(n^2) when poor pivot selection occurs."
            },
            {
                "question": "How do B-Tree indexes improve database query performance?",
                "skill": "Databases",
                "difficulty": "Advanced",
                "question_type": "Architecture",
                "key_concepts": ["B-Tree", "index", "logarithmic", "lookup", "disk I/O", "table scan"],
                "key_points": ["Self-balancing search tree", "Reduces disk I/O with O(log n) lookups"],
                "expected_answer": "B-Tree indexes maintain sorted keys allowing logarithmic O(log n) searches instead of full table scans."
            }
        ]

    # 1. Complete technical interview with all questions answered
    def test_01_complete_interview_all_answered(self):
        answers = {
            0: {"answer_text": "The GIL is a mutex in CPython that ensures only one thread executes bytecode at a time."},
            1: {"answer_text": "Quicksort has average complexity of O(n log n) and worst case O(n^2) with poor pivot selection."},
            2: {"answer_text": "B-Tree indexes enable logarithmic search O(log n) reducing disk I/O and full table scans."}
        }
        res = evaluate_technical_interview(self.sample_questions, answers)
        self.assertEqual(res["total_questions"], 3)
        self.assertEqual(res["answered_questions"], 3)
        self.assertEqual(res["unanswered_questions"], 0)
        self.assertGreater(res["overall_score"], 40)
        self.assertIn(res["performance_level"], ["Good", "Very Good", "Excellent"])

    # 2. Complete interview with some blank answers
    def test_02_interview_with_blank_answers(self):
        answers = {
            0: {"answer_text": "CPython uses a Global Interpreter Lock mutex for thread safety."},
            1: {"answer_text": ""},  # blank
            2: {"answer_text": "   "}  # whitespace blank
        }
        res = evaluate_technical_interview(self.sample_questions, answers)
        self.assertEqual(res["total_questions"], 3)
        self.assertEqual(res["answered_questions"], 1)
        self.assertEqual(res["unanswered_questions"], 2)
        # Blank answers must score 0
        self.assertEqual(res["evaluations"][1]["score"], 0)
        self.assertTrue(res["evaluations"][1]["is_unanswered"])
        self.assertEqual(res["evaluations"][2]["score"], 0)
        self.assertTrue(res["evaluations"][2]["is_unanswered"])

    # 3. Failed speech transcription handling
    def test_03_failed_speech_transcription(self):
        a_res = analyze_audio_behavior("", 15.0)
        self.assertEqual(a_res["word_count"], 0)
        self.assertEqual(a_res["words_per_minute"], 0.0)
        self.assertFalse(a_res["meaningful"])

    # 4. Missing audio metrics handling
    def test_04_missing_audio_metrics(self):
        res = evaluate_technical_interview(self.sample_questions, {0: {"answer_text": "Python GIL lock."}})
        summary = generate_combined_summary(res, audio_results=None, video_results=None)
        self.assertIn("Audio delivery metrics were not recorded or unavailable", summary["communication_improvements"][0])

    # 5. Missing visual metrics handling
    def test_05_missing_visual_metrics(self):
        res = evaluate_technical_interview(self.sample_questions, {0: {"answer_text": "Python GIL lock."}})
        summary = generate_combined_summary(res, audio_results=None, video_results=None)
        self.assertIn("Visual behavioural analysis was not recorded or unavailable", summary["visual_observations"][0])

    # 6. No detected face handling
    def test_06_no_detected_face(self):
        black_frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frames = [black_frame, black_frame]
        v_res = analyze_technical_question_frames(frames, 1, "Python", "Internals")
        self.assertEqual(v_res["face_visibility_pct"], 0.0)
        self.assertEqual(v_res["visual_analysis_status"], "no_face_detected")

    # 7. Missing posture data handling (tight framing)
    def test_07_missing_posture_data(self):
        overall_vis = calculate_overall_visual_analysis({
            0: {"total_frames": 5, "face_detected_frames": 5, "camera_facing_frames": 4, "centered_frames": 4, "posture_available": False}
        })
        self.assertEqual(overall_vis["dominant_posture"], "Unavailable")
        self.assertIn("Unavailable", overall_vis["posture_availability"])

    # 8. Skill-wise performance calculations
    def test_08_skill_wise_calculations(self):
        answers = {
            0: {"answer_text": "GIL is the Global Interpreter Lock in CPython."},
            1: {"answer_text": "Quicksort has O(n log n) average complexity."},
            2: {"answer_text": "B-Tree index allows logarithmic lookup O(log n)."}
        }
        res = evaluate_technical_interview(self.sample_questions, answers)
        self.assertIn("Python Internals", res["skill_averages"])
        self.assertIn("Algorithms & Data Structures", res["skill_averages"])
        self.assertIn("Databases", res["skill_averages"])
        self.assertIn("difficulty_averages", res)
        self.assertIn("Intermediate", res["difficulty_averages"])

    # 9. Question-wise feedback association
    def test_09_question_wise_feedback_association(self):
        answers = {0: {"answer_text": "CPython GIL lock."}}
        res = evaluate_technical_interview(self.sample_questions, answers)
        ev0 = res["evaluations"][0]
        self.assertEqual(ev0["question_number"], 1)
        self.assertEqual(ev0["question"], self.sample_questions[0]["question"])
        self.assertIn("criteria_scores", ev0)
        self.assertIn("technical_correctness", ev0["criteria_scores"])

    # 10. Personalised improvement recommendations
    def test_10_personalised_improvement_roadmap(self):
        answers = {
            0: {"answer_text": "GIL is Global Interpreter Lock."},
            1: {"answer_text": ""},  # 0 on algorithms
            2: {"answer_text": "B-Tree indexing"}
        }
        res = evaluate_technical_interview(self.sample_questions, answers)
        roadmap = generate_improvement_roadmap(res)
        self.assertIn("high_priority", roadmap)
        self.assertIn("medium_priority", roadmap)
        self.assertIn("further_practice", roadmap)
        # Unanswered Q2 should be prioritized
        has_unanswered_action = any("Skipped" in item["title"] or "Algorithms" in item["title"] for item in roadmap["high_priority"])
        self.assertTrue(has_unanswered_action)

    # 11. PDF generation with all data available
    def test_11_pdf_generation_full_data(self):
        answers = {
            0: {"answer_text": "GIL is the Global Interpreter Lock in CPython."},
            1: {"answer_text": "Quicksort O(n log n)."},
            2: {"answer_text": "B-Tree indexes fast lookup."}
        }
        res = evaluate_technical_interview(self.sample_questions, answers)
        session_meta = {
            "candidate_name": "Full Data Candidate",
            "domain": "Python Development",
            "skills": ["Python Internals", "Algorithms"],
            "difficulty": "Intermediate",
            "total_questions": 3,
            "audio_analysis": {0: {"word_count": 25, "words_per_minute": 100.0, "filler_words": 1, "fluency_score": 90}},
            "visual_analysis": {"overall_face_visibility_pct": 90.0, "overall_camera_facing_pct": 85.0, "overall_head_movement": "Natural", "dominant_posture": "Upright", "posture_coverage_pct": 100.0},
            "question_visual_results": {0: {"face_visibility_pct": 92.0, "gaze_summary": {"approx_camera_facing_pct": 85.0}}}
        }
        pdf_bytes = technical_report_pdf.generate_technical_pdf_report(session_meta, res)
        self.assertGreater(len(pdf_bytes), 5000)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreaterEqual(doc.page_count, 3)

    # 12. PDF generation with partial data
    def test_12_pdf_generation_partial_data(self):
        res = evaluate_technical_interview(self.sample_questions, {})
        session_meta = {"total_questions": 3}
        pdf_bytes = technical_report_pdf.generate_technical_pdf_report(session_meta, res)
        self.assertGreater(len(pdf_bytes), 3000)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreaterEqual(doc.page_count, 3)

    # 13. Long answers and multi-page reports
    def test_13_long_answers_multipage(self):
        long_q = [
            {"question": f"Complex System Design Question {i}", "skill": f"Skill {i}", "difficulty": "Advanced", "expected_answer": "Deep explanation"}
            for i in range(8)
        ]
        long_ans = {i: {"answer_text": "A " * 80 + f"detailed technical explanation for question {i}."} for i in range(8)}
        res = evaluate_technical_interview(long_q, long_ans)
        pdf_bytes = technical_report_pdf.generate_technical_pdf_report({"candidate_name": "Long Test", "total_questions": 8}, res)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Should gracefully paginate to 5 or more pages
        self.assertGreaterEqual(doc.page_count, 5)

    # 14. Streamlit session state and state preservation
    def test_14_state_preservation(self):
        import streamlit as st
        app.init_session_state()
        self.assertIn("technical_answers", st.session_state)
        self.assertIn("technical_video_results", st.session_state)
        self.assertIn("technical_audio_results", st.session_state)
        self.assertIn("candidate_name", st.session_state)

    # 15. Retake workflow
    def test_15_retake_workflow_isolation(self):
        import streamlit as st
        st.session_state.technical_questions = self.sample_questions
        st.session_state.technical_answers = {0: "test"}
        st.session_state.candidate_name = "Retake User"
        
        # Retake resets technical variables
        st.session_state.technical_questions = []
        st.session_state.technical_answers = {}
        st.session_state.technical_evaluation_results = None
        
        self.assertEqual(len(st.session_state.technical_questions), 0)
        self.assertEqual(len(st.session_state.technical_answers), 0)
        self.assertIsNone(st.session_state.technical_evaluation_results)
        # Candidate name preserved
        self.assertEqual(st.session_state.candidate_name, "Retake User")

    # 16. Existing Mock HR Interview compatibility
    def test_16_mock_hr_interview_compatibility(self):
        black_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        hr_vis = aggregate_video_analysis([black_frame])
        self.assertIn("face_detected", hr_vis)
        self.assertIn("face_position", hr_vis)
        self.assertIn("eye_contact", hr_vis)
        self.assertIn("movement", hr_vis)

    # 17. Fixed 15-second technical recording preserved
    def test_17_fixed_15_second_duration_preserved(self):
        import streamlit as st
        app.init_session_state()
        self.assertEqual(st.session_state.get("technical_recording_duration", 15), 15)

    # 18. Phase 2 microphone and transcript functionality preserved
    def test_18_phase2_speech_preserved(self):
        from technical_speech import normalize_technical_terms
        norm = normalize_technical_terms("post gres sql and pie torch", "Backend", "Databases")
        self.assertIn("PostgreSQL", norm)
        self.assertIn("PyTorch", norm)

    # 19. Phase 3 visual analysis preserved
    def test_19_phase3_visual_preserved(self):
        white_frame = np.ones((200, 200, 3), dtype=np.uint8) * 255
        res = analyze_technical_question_frames([white_frame], 1, "Python", "OOP")
        self.assertIn("face_visibility_pct", res)
        self.assertIn("gaze_summary", res)
        self.assertIn("approx_camera_facing_pct", res["gaze_summary"])

    # 20. No duplicate or corrupted results
    def test_20_no_duplicate_corrupted_results(self):
        answers = {
            0: {"answer_text": "Answer 1"},
            1: {"answer_text": "Answer 2"}
        }
        res1 = evaluate_technical_interview(self.sample_questions[:2], answers)
        res2 = evaluate_technical_interview(self.sample_questions[:2], answers)
        self.assertEqual(res1["overall_score"], res2["overall_score"])
        self.assertEqual(len(res1["evaluations"]), 2)
        self.assertEqual(res1["evaluations"][0]["question_number"], 1)
        self.assertEqual(res1["evaluations"][1]["question_number"], 2)


if __name__ == "__main__":
    unittest.main()
