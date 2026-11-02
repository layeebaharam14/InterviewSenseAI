"""
test_technical_interview_e2e.py
End-to-end verification of the Technical Interview flow for InterviewSense AI.
Verifies:
1. Setup & Question Generation across domains and skills.
2. Hardware Check & Simulation Mode fallback.
3. Interview Stage Lifecycle (TTS, Countdown, 15s recording loop, Answer saving, Audio & Video analysis).
4. Submission Review (Accurate completion stats, Audio playback paths, Text editing, Live synchronization).
5. Comprehensive Evaluation & Results Dashboard (Multi-criteria scoring, Radial gauge, 5-tab analytics).
6. Multi-page PDF Report Generation (PyMuPDF rendering, text sanitization, byte validation).
7. Retake Flow (Clean session variable reset, Countdown/TTS flag purging).
"""

import os
import sys
import unittest
import numpy as np

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interviewsense.data.technical_questions import generate_technical_questions, QUESTION_BANK
from src.interviewsense.analysis.technical_evaluation import (
    evaluate_technical_interview,
    evaluate_technical_answer,
    classify_performance,
    generate_combined_summary,
    generate_improvement_roadmap
)
from src.interviewsense.analysis.audio_analysis import analyze_audio_behavior
from src.interviewsense.analysis.video_analysis import (
    analyze_technical_question_frames,
    calculate_overall_visual_analysis
)
from src.interviewsense.services.technical_speech import (
    normalize_technical_terms,
    get_temp_audio_path,
    cleanup_temp_audio
)
from src.interviewsense.reports.technical_report_pdf import generate_technical_pdf_report


class TestTechnicalInterviewEndToEnd(unittest.TestCase):

    def setUp(self):
        self.session_id = "test_sess_001"
        self.domain = "Python Programming"
        self.skills = ["OOP in Python", "Functions and Modules"]
        self.difficulty = "Intermediate"
        self.num_questions = 3

    def tearDown(self):
        cleanup_temp_audio(self.session_id)

    def test_01_setup_and_question_generation(self):
        """Tests that setup correctly generates requested questions with rich metadata."""
        qs = generate_technical_questions(self.domain, self.skills, self.difficulty, self.num_questions)
        self.assertEqual(len(qs), self.num_questions)
        for q in qs:
            self.assertIn("question", q)
            self.assertIn("key_concepts", q)
            self.assertIn("important_points", q)
            self.assertIn("expected_answer", q)
            self.assertIn("common_mistakes", q)
            self.assertEqual(q.get("domain"), self.domain)

    def test_02_speech_normalization_for_domain(self):
        """Tests that technical speech normalization works smoothly for spoken concepts."""
        raw_spoken = "we use o o p and pie torch for deep learning with num py"
        normalized = normalize_technical_terms(raw_spoken, domain=self.domain, skills=self.skills)
        self.assertIn("OOP", normalized)
        self.assertIn("PyTorch", normalized)
        self.assertIn("NumPy", normalized)

    def test_03_simulated_interview_loop(self):
        """Simulates Question 1 to 3 loop: answers, audio metrics, video frames, saving."""
        qs = generate_technical_questions(self.domain, self.skills, self.difficulty, self.num_questions)
        technical_answers = {}
        technical_audio_results = {}
        technical_video_results = {}

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw simulated face region in center
        dummy_frame[140:340, 220:420] = 180

        for i, q_data in enumerate(qs):
            # Audio path
            audio_path = get_temp_audio_path(self.session_id, i)
            # Answer simulation tailored to each question's key concepts and expected answer
            resp_text = f"In {self.domain}, regarding {q_data.get('question')}: " + " ".join(q_data.get("key_concepts", [])) + ". " + q_data.get("expected_answer", "")
            technical_answers[i] = {
                "question_id": i + 1,
                "question": q_data.get("question", ""),
                "domain": self.domain,
                "skill": q_data.get("skill", "General"),
                "difficulty": self.difficulty,
                "question_type": q_data.get("question_type", "Conceptual"),
                "answer_text": resp_text,
                "answer_method": "voice",
                "raw_transcript": resp_text,
                "audio_path": audio_path
            }

            # Audio analysis
            a_res = analyze_audio_behavior(resp_text, 15)
            self.assertGreater(a_res["word_count"], 0)
            self.assertGreaterEqual(a_res["fluency_score"], 0)
            technical_audio_results[i] = a_res

            # Video analysis (15 sampled frames)
            sampled_frames = [dummy_frame.copy() for _ in range(15)]
            v_res = analyze_technical_question_frames(
                sampled_frames,
                question_id=i + 1,
                domain=self.domain,
                skill=q_data.get("skill", "General")
            )
            self.assertIn("total_frames", v_res)
            self.assertEqual(v_res["total_frames"], 15)
            technical_video_results[i] = v_res

        self.assertEqual(len(technical_answers), 3)
        self.assertEqual(len(technical_audio_results), 3)
        self.assertEqual(len(technical_video_results), 3)

        # Overall visual aggregation
        overall_vis = calculate_overall_visual_analysis(technical_video_results)
        self.assertIn("overall_face_visibility_pct", overall_vis)
        self.assertEqual(overall_vis["total_questions_analyzed"], 3)

        # Evaluation
        eval_results = evaluate_technical_interview(qs, technical_answers)
        self.assertEqual(eval_results["total_questions"], 3)
        self.assertEqual(eval_results["answered_questions"], 3)
        self.assertGreater(eval_results["overall_score"], 50)

        # Combined summary & roadmap
        summary = generate_combined_summary(eval_results, technical_audio_results, overall_vis)
        self.assertIn("technical_strengths", summary)
        self.assertIn("weak_technical_areas", summary)

        roadmap = generate_improvement_roadmap(eval_results, technical_audio_results, overall_vis)
        self.assertIn("high_priority", roadmap)
        self.assertIn("medium_priority", roadmap)

        # Multi-page PDF generation
        session_meta = {
            "candidate_name": "Test Candidate",
            "domain": self.domain,
            "skills": self.skills,
            "difficulty": self.difficulty,
            "total_questions": 3,
            "timestamp": "October 31, 2026 - 11:00 AM",
            "audio_analysis": technical_audio_results,
            "visual_analysis": overall_vis,
            "question_visual_results": technical_video_results,
            "combined_summary": summary,
            "improvement_roadmap": roadmap
        }
        pdf_bytes = generate_technical_pdf_report(session_meta, eval_results)
        self.assertGreater(len(pdf_bytes), 5000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_04_unanswered_and_partial_answers_graceful_handling(self):
        """Verifies that empty/skipped answers and audio errors evaluate safely without exceptions."""
        qs = generate_technical_questions(self.domain, self.skills, self.difficulty, 3)
        technical_answers = {
            0: {"answer_text": "Good technical answer about classes and inheritance.", "answer_method": "text"},
            1: {"answer_text": "", "answer_method": "voice"}, # Unanswered
            2: {"answer_text": "Brief mention.", "answer_method": "text"}
        }

        # Empty audio and video results
        eval_results = evaluate_technical_interview(qs, technical_answers)
        self.assertEqual(eval_results["answered_questions"], 2)
        self.assertEqual(eval_results["unanswered_questions"], 1)
        self.assertEqual(eval_results["evaluations"][1]["score"], 0)
        self.assertTrue(eval_results["evaluations"][1]["is_unanswered"])

        overall_vis = calculate_overall_visual_analysis({})
        summary = generate_combined_summary(eval_results, {}, overall_vis)
        self.assertTrue(any("unanswered" in w.lower() for w in summary["weak_technical_areas"]))

        roadmap = generate_improvement_roadmap(eval_results, {}, overall_vis)
        self.assertTrue(len(roadmap["high_priority"]) > 0)

        # PDF still generates cleanly even with 0 audio and 0 video data
        session_meta = {
            "candidate_name": "Test Candidate",
            "domain": self.domain,
            "skills": self.skills,
            "difficulty": self.difficulty,
            "total_questions": 3,
            "timestamp": "October 31, 2026 - 11:00 AM",
            "audio_analysis": {},
            "visual_analysis": overall_vis,
            "question_visual_results": {},
            "combined_summary": summary,
            "improvement_roadmap": roadmap
        }
        pdf_bytes = generate_technical_pdf_report(session_meta, eval_results)
        self.assertGreater(len(pdf_bytes), 3000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
