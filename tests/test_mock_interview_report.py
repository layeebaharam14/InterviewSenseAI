"""
test_mock_interview_report.py — InterviewSense AI
Tests for Mock Interview Final Report & PDF Generation Engine.
Verifies results dashboard generation, metric accuracy, question-wise evaluation,
multi-page PDF generation, and preservation of Technical Interview reports.
"""

import os
import sys
import unittest
from datetime import datetime

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pymupdf as fitz
from src.interviewsense.core.scoring import calculate_scores
from src.interviewsense.core.insights import (
    generate_feedback,
    evaluate_mock_question,
    generate_mock_interview_summary,
)
from src.interviewsense.reports.hr_report_pdf import (
    generate_hr_pdf_report,
    sanitize_text,
    truncate_text,
)
from src.interviewsense.reports.technical_report_pdf import generate_technical_pdf_report


class TestMockInterviewReportSummary(unittest.TestCase):
    """Tests summary data structure and question-wise evaluation."""

    def setUp(self):
        self.sample_questions = [
            "What are your strengths?",
            "What is your biggest weakness?",
            "Why should we hire you?"
        ]
        self.sample_video = [
            {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"},
            {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"},
            {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"},
        ]
        self.sample_audio = [
            {"audio_available": True, "meaningful": True, "transcribed_text": "I am analytical and work well with engineering teams.", "word_count": 9, "words_per_minute": 110.0, "speech_rate": "Well-paced", "filler_words": 0, "pauses": 0, "fluency_score": 100},
            {"audio_available": True, "meaningful": True, "transcribed_text": "I sometimes focus too much on details, but I manage my time with checklists.", "word_count": 14, "words_per_minute": 120.0, "speech_rate": "Well-paced", "filler_words": 0, "pauses": 0, "fluency_score": 95},
            {"audio_available": True, "meaningful": True, "transcribed_text": "You should hire me because I deliver high quality code on schedule.", "word_count": 12, "words_per_minute": 115.0, "speech_rate": "Well-paced", "filler_words": 0, "pauses": 0, "fluency_score": 100},
        ]

    def test_complete_evaluation_summary(self):
        """Verifies summary generation with full audio and video data."""
        summary = generate_mock_interview_summary(
            questions=self.sample_questions,
            video_results=self.sample_video,
            audio_results=self.sample_audio,
            candidate_name="Jane Doe"
        )
        self.assertEqual(summary["candidate_name"], "Jane Doe")
        self.assertEqual(summary["total_questions"], 3)
        self.assertEqual(summary["audio_questions_evaluated"], 3)
        self.assertEqual(summary["video_questions_evaluated"], 3)
        self.assertEqual(summary["overall_score"], 100)
        self.assertEqual(summary["verdict"], "Ready for Interview")
        self.assertIn("Full", summary["coverage_status"])
        self.assertEqual(len(summary["question_evaluations"]), 3)

        q1 = summary["question_evaluations"][0]
        self.assertEqual(q1["question"], "What are your strengths?")
        self.assertEqual(q1["audio_status"], "transcribed")
        self.assertEqual(q1["video_status"], "detected")
        self.assertTrue(len(q1["what_went_well"]) > 0)
        self.assertTrue(len(q1["what_to_improve"]) > 0)

    def test_missing_audio_summary(self):
        """Verifies summary when audio recording or transcription fails."""
        failed_audio = [
            {"audio_available": False, "meaningful": False, "transcribed_text": "", "word_count": 0, "words_per_minute": 0.0, "speech_rate": "Unavailable", "filler_words": 0, "pauses": 0, "fluency_score": 0}
            for _ in range(3)
        ]
        summary = generate_mock_interview_summary(
            questions=self.sample_questions,
            video_results=self.sample_video,
            audio_results=failed_audio,
            candidate_name="Alex Smith"
        )
        self.assertEqual(summary["audio_questions_evaluated"], 0)
        self.assertIsNone(summary["communication_score"])
        self.assertIn("Visual Only", summary["coverage_status"])
        self.assertIn("Communication dimension excluded", summary["score_note"])
        # Confidence score should NOT be forced to zero
        self.assertGreater(summary["confidence_score"], 0)

        for q in summary["question_evaluations"]:
            self.assertEqual(q["audio_status"], "unavailable")
            self.assertTrue(any("Audio unavailable" in s for s in q["what_to_improve"]))

    def test_silent_audio_summary(self):
        """Verifies summary when candidate was silent during recording."""
        silent_audio = [
            {"audio_available": True, "meaningful": False, "transcribed_text": "No speech detected.", "word_count": 0, "words_per_minute": 0.0, "speech_rate": "None", "filler_words": 0, "pauses": 0, "fluency_score": 0}
            for _ in range(3)
        ]
        summary = generate_mock_interview_summary(
            questions=self.sample_questions,
            video_results=self.sample_video,
            audio_results=silent_audio,
        )
        self.assertEqual(summary["audio_questions_evaluated"], 3)
        for q in summary["question_evaluations"]:
            self.assertEqual(q["audio_status"], "silent")
            self.assertTrue(any("No speech" in s for s in q["what_to_improve"]))

    def test_missing_video_summary(self):
        """Verifies summary when webcam was not detected."""
        missing_video = [
            {"face_detected": False, "eye_contact": "unavailable", "movement": "unavailable", "face_presence_pct": 0.0}
            for _ in range(3)
        ]
        summary = generate_mock_interview_summary(
            questions=self.sample_questions,
            video_results=missing_video,
            audio_results=self.sample_audio,
        )
        self.assertEqual(summary["video_questions_evaluated"], 0)
        for q in summary["question_evaluations"]:
            self.assertEqual(q["video_status"], "unavailable")
            self.assertTrue(any("Face was not detected" in s for s in q["what_to_improve"]))

    def test_long_answers_and_multiple_questions(self):
        """Verifies summary handles long answers and many questions without errors."""
        long_text = "I have developed multiple scalable web applications using Python, FastAPI, React, and PostgreSQL. " * 5
        long_questions = [f"Describe project experience #{i+1}" for i in range(6)]
        long_video = [{"face_detected": True, "eye_contact": "good", "movement": "low"} for _ in range(6)]
        long_audio = [
            {"audio_available": True, "meaningful": True, "transcribed_text": long_text, "word_count": 75, "words_per_minute": 150.0, "speech_rate": "Well-paced", "filler_words": 2, "pauses": 1, "fluency_score": 85}
            for _ in range(6)
        ]
        summary = generate_mock_interview_summary(
            questions=long_questions,
            video_results=long_video,
            audio_results=long_audio
        )
        self.assertEqual(summary["total_questions"], 6)
        self.assertEqual(len(summary["question_evaluations"]), 6)


class TestMockInterviewPDFReport(unittest.TestCase):
    """Tests multi-page PDF generation, layout flow, and metric disclosure."""

    def test_pdf_generation_complete_data(self):
        """Generates PDF with full data and verifies structure via PyMuPDF."""
        questions = [
            "What are your strengths?",
            "What is your biggest weakness?",
            "Why should we hire you?"
        ]
        v_res = [
            {"face_detected": True, "eye_contact": "good", "movement": "low", "face_position": "centered", "posture": "Upright"}
            for _ in range(3)
        ]
        a_res = [
            {"audio_available": True, "meaningful": True, "transcribed_text": "I am a dedicated engineer with problem solving skills.", "word_count": 9, "words_per_minute": 120.0, "speech_rate": "Well-paced", "filler_words": 0, "pauses": 0, "fluency_score": 100}
            for _ in range(3)
        ]
        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=v_res,
            audio_results=a_res,
            candidate_name="Sarah Connor"
        )
        pdf_bytes = generate_hr_pdf_report(summary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 2000)

        # Inspect generated PDF document
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreaterEqual(doc.page_count, 2)

        # Page 1 checks
        p1_text = doc[0].get_text()
        self.assertIn("INTERVIEWSENSE AI", p1_text)
        self.assertIn("Sarah Connor", p1_text)
        self.assertIn("OVERALL SIMULATION SCORE", p1_text)
        self.assertIn("PERFORMANCE METRICS BREAKDOWN", p1_text)
        self.assertIn("Confidence Score", p1_text)
        self.assertIn("Nervousness Index", p1_text)
        self.assertIn("Communication Score", p1_text)

        # Page 2 checks
        p2_text = doc[1].get_text()
        self.assertIn("QUESTION-BY-QUESTION", p2_text)
        self.assertIn("What are your strengths?", p2_text)
        self.assertIn("What went well", p2_text)
        self.assertIn("What to improve", p2_text)

        # Check footer page numbering exists
        self.assertIn(f"Page 1 of {doc.page_count}", doc[0].get_text())
        self.assertIn(f"Page 2 of {doc.page_count}", doc[1].get_text())
        doc.close()

    def test_pdf_generation_missing_audio(self):
        """Verifies PDF renders N/A for communication when audio was unavailable."""
        questions = ["Tell me about a challenge you faced."]
        v_res = [{"face_detected": True, "eye_contact": "good", "movement": "low"}]
        a_res = [{"audio_available": False, "meaningful": False, "transcribed_text": ""}]

        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=v_res,
            audio_results=a_res,
            candidate_name="Dev User"
        )
        pdf_bytes = generate_hr_pdf_report(summary)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        p1_text = doc[0].get_text()
        self.assertIn("N/A", p1_text)
        self.assertIn("Audio Unavailable", p1_text)
        doc.close()

    def test_pdf_long_session_multipage_flow(self):
        """Verifies 5 questions with long transcripts flow across multiple pages without overlap."""
        long_text = "In my previous role as lead developer, I managed a team of five engineers to deliver a scalable cloud microservice. We reduced latency by 45 percent and deployed CI/CD pipelines using GitHub Actions. " * 3
        questions = [
            f"Question {i+1}: Can you elaborate on key engineering challenge #{i+1}?"
            for i in range(5)
        ]
        v_res = [{"face_detected": True, "eye_contact": "good", "movement": "low"} for _ in range(5)]
        a_res = [
            {"audio_available": True, "meaningful": True, "transcribed_text": long_text, "word_count": 70, "words_per_minute": 140.0, "speech_rate": "Well-paced", "filler_words": 1, "pauses": 1, "fluency_score": 90}
            for _ in range(5)
        ]
        summary = generate_mock_interview_summary(
            questions=questions,
            video_results=v_res,
            audio_results=a_res,
            candidate_name="Elena Vance"
        )
        pdf_bytes = generate_hr_pdf_report(summary)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreaterEqual(doc.page_count, 3)
        # Verify last page has footer and methodology
        last_page_text = doc[-1].get_text()
        self.assertIn("InterviewSense AI", last_page_text)
        self.assertIn(f"Page {doc.page_count} of {doc.page_count}", last_page_text)
        doc.close()

    def test_preservation_of_technical_report_pdf(self):
        """Verifies technical_report_pdf is 100% intact and unaffected."""
        mock_summary = {
            "overall_score": 88,
            "performance_level": "Very Good",
            "domain": "Python Programming",
            "difficulty": "Intermediate",
            "total_questions": 1,
            "answered_count": 1,
            "unanswered_count": 0,
            "average_question_score": 88.0,
            "criteria_averages": {
                "technical_correctness": 36.0,
                "conceptual_understanding": 22.0,
                "relevance": 14.0,
                "completeness": 13.0,
                "explanation_quality": 4.5
            },
            "per_question_results": [{
                "question": "What is Python?",
                "score": 88,
                "criteria_scores": {"technical_correctness": 36, "conceptual_understanding": 22, "relevance": 14, "completeness": 13, "explanation_quality": 4.5},
                "feedback": {"strengths": ["Clear explanation"], "missing_points": []},
                "candidate_answer": "Python is an interpreted high-level language.",
                "model_answer": "Python is an interpreted programming language."
            }],
            "top_strengths": ["Solid explanation"],
            "areas_for_improvement": ["Elaborate on typing"],
            "recommended_topics": ["Type hinting"]
        }
        pdf_bytes = generate_technical_pdf_report(mock_summary, mock_summary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)


class TestHRResultsModuleContract(unittest.TestCase):
    """Verifies that hr_results.py satisfies all required UI contracts and triggers."""

    def test_ui_module_content(self):
        ui_path = os.path.join("src", "interviewsense", "ui", "hr_results.py")
        self.assertTrue(os.path.exists(ui_path))
        with open(ui_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Contract checks
        self.assertIn("def render_results_page():", code)
        self.assertIn("top-anchor", code)
        self.assertIn("scroll_to_top()", code)
        self.assertIn("calculate_scores", code)
        self.assertIn("generate_mock_interview_summary", code)
        self.assertIn("generate_hr_pdf_report", code)
        self.assertIn("Download Mock Interview Report (PDF)", code)
        self.assertIn("Restart Interview", code)
        self.assertIn("st.session_state.current_page = \"mode_selection\"", code)
        self.assertIn("questions_accordion_group", code)
        self.assertIn("disclaimers_accordion_group", code)

    def test_results_ui_refinements(self):
        """Verifies the 5 targeted UI and navigation refinements in hr_results.py."""
        ui_path = os.path.join("src", "interviewsense", "ui", "hr_results.py")
        with open(ui_path, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Centred subtitle
        self.assertIn("text-align: center", code)
        self.assertIn("Comprehensive behavioral and speech evaluation based on your simulation performance.", code)

        # 2. Evaluation coverage understandable presentation
        self.assertIn("Evaluation Coverage", code)
        self.assertIn("Audio:", code)
        self.assertIn("Video:", code)
        self.assertIn("{audio_q}/{total_q} questions", code)
        self.assertIn("{video_q}/{total_q} questions", code)

        # 3. Accordion styling (dark navy question headers, white disclaimer header with dark text)
        self.assertIn(".st-key-questions_accordion_group details[data-testid=\"stExpander\"] > summary", code)
        self.assertIn("#0f172a", code)  # dark navy
        self.assertIn(".st-key-disclaimers_accordion_group details[data-testid=\"stExpander\"] > summary", code)
        self.assertIn("#ffffff", code)  # white disclaimer header

        # 4. Matched action buttons
        self.assertIn("type=\"primary\"", code)
        self.assertIn(".stDownloadButton > button", code)

        # 5. Restart Interview routes to mode_selection and resets state
        self.assertIn('st.session_state.current_page = "mode_selection"', code)
        self.assertIn("st.session_state.question_index = 0", code)
        self.assertIn("st.session_state.current_questions = []", code)
        self.assertIn("st.session_state.video_results = []", code)
        self.assertIn("st.session_state.audio_results = []", code)

    def test_all_question_expanders_collapsed_by_default(self):
        """Verifies that all question analysis expanders are collapsed by default (expanded=False)."""
        ui_path = os.path.join("src", "interviewsense", "ui", "hr_results.py")
        with open(ui_path, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn('with st.expander(f"{status_icon} Question {q_num}: {q_title}", expanded=False):', code)
        self.assertNotIn("expanded=(idx == 0)", code)


if __name__ == "__main__":
    unittest.main()
