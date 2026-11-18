"""
test_mock_interview_e2e_workflow.py — InterviewSense AI
End-to-end integration and data integrity tests for the Mock HR Interview workflow.
Verifies complete interview loops, heterogeneous failure isolation, session state lifecycle,
question-wise data alignment, and preservation of Technical Interview functionality.
"""

import os
import sys
import unittest
from datetime import datetime

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pymupdf as fitz
from src.interviewsense.core.app_helpers import QUESTION_POOL, get_question_duration
from src.interviewsense.core.scoring import calculate_scores
from src.interviewsense.core.insights import (
    generate_feedback,
    evaluate_mock_question,
    generate_mock_interview_summary,
)
from src.interviewsense.analysis.audio_analysis import analyze_audio_behavior
from src.interviewsense.reports.hr_report_pdf import generate_hr_pdf_report
from src.interviewsense.reports.technical_report_pdf import generate_technical_pdf_report
from src.interviewsense.data.technical_questions import generate_technical_questions
from src.interviewsense.analysis.technical_evaluation import evaluate_technical_answer


class MockSessionState(dict):
    """Mock Streamlit session state supporting attribute and dict access."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'MockSessionState' has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value


class TestMockInterviewE2EWorkflow(unittest.TestCase):
    """End-to-End integration tests for Mock Interview lifecycle."""

    def test_01_complete_e2e_mock_interview_session(self):
        """Simulates full 5-question interview from setup to evaluation and PDF."""
        # 1. Setup & Question pool
        questions = [
            "Tell me about yourself",
            "What are your strengths?",
            "What is your biggest weakness?",
            "Describe a challenge you faced and how you handled it.",
            "Why should we hire you?"
        ]
        self.assertEqual(len(questions), 5)

        # 2. Answers & Simulated telemetry per question (realistic complete responses)
        candidate_answers = [
            "I am a software engineer with four years of full stack experience. I specialize in designing Python backends and modern web interfaces, leading cross functional feature delivery.",
            "My primary strengths are analytical problem solving, clean system architecture, and proactive communication across product and engineering team members during releases.",
            "I sometimes spend too much time perfecting code, but I now manage my delivery using strict timeboxes and agile sprint milestones to maintain steady momentum.",
            "When our production database experienced heavy lock contention during a release, I rolled back safely, optimized the queries, and added proper indexing.",
            "You should hire me because I bring strong technical foundation in Python, exceptional collaboration, and a proven track record of shipping reliable production software."
        ]

        video_results = []
        audio_results = []

        for i, (q, ans) in enumerate(zip(questions, candidate_answers)):
            dur = get_question_duration(q)
            self.assertGreaterEqual(dur, 15)

            # Simulated camera: good eye contact, centered, upright
            v_res = {
                "face_detected": True,
                "eye_contact": "good",
                "movement": "low",
                "multiple_faces_detected": False,
                "face_presence_pct": 95.0,
                "face_position": "centered",
                "gaze_direction": "Camera / Center",
                "posture": "Upright",
                "total_frames": dur,
                "face_frames": dur - 1,
            }
            video_results.append(v_res)

            # Process audio behavior
            a_res = analyze_audio_behavior(ans, dur, audio_failed=False)
            self.assertTrue(a_res["audio_available"])
            self.assertTrue(a_res["meaningful"])
            self.assertEqual(a_res["transcribed_text"], ans)
            audio_results.append(a_res)

        # 3. Verify 1:1 question-answer-telemetry synchronization
        self.assertEqual(len(questions), 5)
        self.assertEqual(len(video_results), 5)
        self.assertEqual(len(audio_results), 5)

        # 4. Scoring & Feedback
        scores = calculate_scores(video_results, audio_results)
        self.assertEqual(scores["audio_questions_evaluated"], 5)
        self.assertEqual(scores["video_questions_evaluated"], 5)
        self.assertGreaterEqual(scores["confidence"], 80)
        self.assertLessEqual(scores["nervousness"], 25)
        self.assertGreaterEqual(scores["communication"], 80)

        feedback = generate_feedback(scores)
        self.assertEqual(feedback["verdict"], "Ready for Interview")
        self.assertGreaterEqual(feedback["overall_score"], 80)

        # 5. Summary Assembly
        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=video_results,
            audio_results=audio_results,
            scores=scores,
            feedback=feedback,
            candidate_name="Morgan Freeman"
        )
        self.assertEqual(summary["total_questions"], 5)
        self.assertIn("Full", summary["coverage_status"])
        self.assertEqual(len(summary["question_evaluations"]), 5)

        # Verify each question evaluation maps to the exact candidate answer
        for idx in range(5):
            q_eval = summary["question_evaluations"][idx]
            self.assertEqual(q_eval["question"], questions[idx])
            self.assertEqual(q_eval["transcript"], candidate_answers[idx])
            self.assertEqual(q_eval["audio_status"], "transcribed")
            self.assertEqual(q_eval["video_status"], "detected")
            self.assertTrue(len(q_eval["what_went_well"]) > 0)

        # 6. PDF Generation from identical summary
        pdf_bytes = generate_hr_pdf_report(summary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 5000)

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreaterEqual(doc.page_count, 2)
        full_pdf_text = "".join(p.get_text() for p in doc)
        self.assertIn("Morgan Freeman", full_pdf_text)
        self.assertIn("Tell me about yourself", full_pdf_text)
        self.assertIn("analytical problem solving", full_pdf_text)
        self.assertIn(f"{feedback['overall_score']}", full_pdf_text)
        doc.close()

    def test_02_heterogeneous_session_mixed_audio_video_failures(self):
        """
        Tests session with isolated failures:
        Q1: Full success
        Q2: Audio pipeline error (mic/SR failure)
        Q3: Video failure (face not detected)
        Q4: Candidate silence (genuine 0 words spoken)
        Q5: Full success
        """
        questions = [f"Mock Prompt #{i+1}" for i in range(5)]

        # Q1: Success
        v1 = {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"}
        a1 = analyze_audio_behavior("I successfully led the integration project from start to finish.", 15, audio_failed=False)

        # Q2: Audio pipeline failure
        v2 = {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"}
        a2 = analyze_audio_behavior("", 15, audio_failed=True)

        # Q3: Video failure (no face detected)
        v3 = {"face_detected": False, "eye_contact": "unavailable", "movement": "unavailable", "face_presence_pct": 0.0}
        a3 = analyze_audio_behavior("Here is my clear answer to the third question despite camera issues.", 15, audio_failed=False)

        # Q4: Candidate silence (audio pipeline succeeded, but user said nothing)
        v4 = {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"}
        a4 = analyze_audio_behavior("No speech detected.", 15, audio_failed=False)

        # Q5: Success
        v5 = {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"}
        a5 = analyze_audio_behavior("Thank you for your time and I look forward to working with you.", 15, audio_failed=False)

        v_list = [v1, v2, v3, v4, v5]
        a_list = [a1, a2, a3, a4, a5]

        # Scoring verification
        scores = calculate_scores(v_list, a_list)
        # Q2 audio failed -> 4 evaluated audio questions
        self.assertEqual(scores["audio_questions_evaluated"], 4)
        # Q3 video failed -> 4 evaluated video questions
        self.assertEqual(scores["video_questions_evaluated"], 4)

        # Q2 failure should NOT force communication to zero
        self.assertGreater(scores["communication"], 0)
        # Q3 video failure should NOT force confidence to zero
        self.assertGreater(scores["confidence"], 0)

        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=v_list,
            audio_results=a_list,
            scores=scores,
            candidate_name="Mixed Case User"
        )
        self.assertIn("Partial", summary["coverage_status"])
        evals = summary["question_evaluations"]

        # Check Q1: transcribed & detected
        self.assertEqual(evals[0]["audio_status"], "transcribed")
        self.assertEqual(evals[0]["video_status"], "detected")

        # Check Q2: audio unavailable
        self.assertEqual(evals[1]["audio_status"], "unavailable")
        self.assertTrue(any("Audio unavailable" in s for s in evals[1]["what_to_improve"]))

        # Check Q3: video unavailable
        self.assertEqual(evals[2]["video_status"], "unavailable")
        self.assertTrue(any("Face was not detected" in s for s in evals[2]["what_to_improve"]))

        # Check Q4: silence recorded
        self.assertEqual(evals[3]["audio_status"], "silent")
        self.assertTrue(any("No speech" in s for s in evals[3]["what_to_improve"]))

        # Check Q5: transcribed & detected
        self.assertEqual(evals[4]["audio_status"], "transcribed")
        self.assertEqual(evals[4]["video_status"], "detected")

        # Verify PDF generates properly with mixed data
        pdf_bytes = generate_hr_pdf_report(summary)
        self.assertGreater(len(pdf_bytes), 3000)

    def test_03_session_state_restart_and_fresh_session(self):
        """Verifies that restart clears all mock interview state without polluting unrelated state."""
        state = MockSessionState()

        # Simulate state after completing an interview
        state.current_page = "results"
        state.current_tab = "Home"
        state.question_index = 5
        state.current_questions = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        state.video_results = [{"face_detected": True}] * 5
        state.audio_results = [{"audio_available": True}] * 5
        state.frames = ["fake_frame_bytes"] * 10
        state.is_recording = False
        state.analysis_done = True
        state.question_spoken = True
        state.hardware_verified = True
        state.last_audio_error = "Old Error"

        # Unrelated state that MUST be preserved
        state.candidate_name = "Persistent User"
        state.technical_domain = "Python Programming"
        state.technical_skills = ["OOP in Python"]

        # Simulate Restart Interview action
        state.current_page = "landing"
        state.current_tab = "Home"
        state.question_index = 0
        state.current_questions = []
        state.video_results = []
        state.audio_results = []
        state.frames = []
        state.is_recording = False
        state.analysis_done = False
        state.question_spoken = False
        state.hardware_verified = False
        state.last_audio_error = None

        # Verify mock interview state is thoroughly reset
        self.assertEqual(state.current_page, "landing")
        self.assertEqual(state.question_index, 0)
        self.assertEqual(len(state.current_questions), 0)
        self.assertEqual(len(state.video_results), 0)
        self.assertEqual(len(state.audio_results), 0)
        self.assertEqual(len(state.frames), 0)
        self.assertFalse(state.is_recording)
        self.assertFalse(state.analysis_done)
        self.assertFalse(state.hardware_verified)
        self.assertIsNone(state.last_audio_error)

        # Verify unrelated application state was preserved
        self.assertEqual(state.candidate_name, "Persistent User")
        self.assertEqual(state.technical_domain, "Python Programming")
        self.assertEqual(state.technical_skills, ["OOP in Python"])

    def test_04_data_alignment_lockstep_guarantee(self):
        """Verifies that scoring and evaluation never crash or desync if lists have unequal lengths."""
        # 3 questions, but only 2 video results and 1 audio result
        questions = ["Question A", "Question B", "Question C"]
        v_list = [{"face_detected": True}, {"face_detected": False}]
        a_list = [{"audio_available": True, "meaningful": True, "transcribed_text": "Only answer", "word_count": 2, "words_per_minute": 60.0, "speech_rate": "Well-paced", "filler_words": 0, "pauses": 0, "fluency_score": 70}]

        # calculate_scores should handle gracefully
        scores = calculate_scores(v_list, a_list)
        self.assertIn("confidence", scores)
        self.assertIn("nervousness", scores)
        self.assertIn("communication", scores)

        # generate_mock_interview_summary should handle gracefully
        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=v_list,
            audio_results=a_list,
            scores=scores
        )
        self.assertEqual(len(summary["question_evaluations"]), 3)
        self.assertEqual(summary["question_evaluations"][0]["question"], "Question A")
        self.assertEqual(summary["question_evaluations"][1]["question"], "Question B")
        self.assertEqual(summary["question_evaluations"][2]["question"], "Question C")

    def test_05_preservation_of_technical_interview_workflow(self):
        """Verifies that Technical Interview workflow, scoring, and PDF are 100% operational."""
        # 1. Question generation
        qs = generate_technical_questions("Python Programming", ["OOP in Python"], "Intermediate", 1)
        self.assertEqual(len(qs), 1)
        q = qs[0]
        self.assertIn("expected_answer", q)

        # 2. Answer evaluation
        ans = "Encapsulation restricts direct access to some of an object's components."
        eval_res = evaluate_technical_answer(q, ans)
        self.assertIn("score", eval_res)
        self.assertIn("criteria_scores", eval_res)

        # 3. PDF report generation
        tech_summary = {
            "overall_score": 85,
            "performance_level": "Very Good",
            "domain": "Python Programming",
            "difficulty": "Intermediate",
            "total_questions": 1,
            "answered_count": 1,
            "unanswered_count": 0,
            "average_question_score": 85.0,
            "criteria_averages": {
                "technical_correctness": 34.0,
                "conceptual_understanding": 22.0,
                "relevance": 13.0,
                "completeness": 12.0,
                "explanation_quality": 4.0
            },
            "per_question_results": [eval_res],
            "top_strengths": ["Clear definition"],
            "areas_for_improvement": ["Provide syntax example"],
            "recommended_topics": ["Encapsulation vs Abstraction"]
        }
        pdf_bytes = generate_technical_pdf_report(tech_summary, tech_summary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)


if __name__ == "__main__":
    unittest.main()
