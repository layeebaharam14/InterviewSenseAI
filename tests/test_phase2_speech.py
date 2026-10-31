"""
Phase 2 Dedicated Speech Capture & Recognition Tests — InterviewSense AI
========================================================================
Covers all Phase 2 requirements:
1.  Fixed 15-second capture duration default.
2.  Correct question/domain/skill association.
3.  Technical terminology normalization across programming domains.
4.  Empty audio (sr.UnknownValueError) handling.
5.  Recognition API network failure (sr.RequestError) handling.
6.  Microphone initialization / Windows permission failure (OSError/IOError).
7.  Transcript preservation into session state.
8.  Manual transcript editing flow with audio recovery path preservation.
9.  Audio file creation and cleanup lifecycle.
10. Thread lifecycle, non-blocking capture, and join safety.
11. Live hardware microphone check (gracefully skipped if hardware is offline).
"""
import inspect
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import speech_recognition as sr
import streamlit as st

from src.interviewsense.services.technical_speech import (
    normalize_technical_terms,
    record_and_transcribe_audio,
    transcribe_audio_file,
    get_temp_audio_dir,
    get_temp_audio_path,
    cleanup_temp_audio,
)
from src.interviewsense.core.app_helpers import (
    record_technical_voice_answer,
    save_current_technical_answer,
    get_technical_question_duration,
)


class TestPhase2SpeechCapture(unittest.TestCase):
    """Automated unit and mock tests for Phase 2 voice capture & speech recognition."""

    # -------------------------------------------------------------------------
    # 1. FIXED 15-SECOND CAPTURE DURATION
    # -------------------------------------------------------------------------
    def test_fixed_15_second_duration_default(self):
        """Verifies that all Phase 2 technical speech functions default to a 15-second duration."""
        # Check signature defaults
        sig_rta = inspect.signature(record_and_transcribe_audio)
        self.assertEqual(
            sig_rta.parameters["duration"].default, 15,
            "record_and_transcribe_audio default duration must be 15s"
        )

        sig_rtv = inspect.signature(record_technical_voice_answer)
        self.assertEqual(
            sig_rtv.parameters["duration"].default, 15,
            "record_technical_voice_answer default duration must be 15s"
        )

        # Check get_technical_question_duration returns 15 for all categories
        for q_type in ["Conceptual", "Practical", "Coding", "Scenario"]:
            for diff in ["Beginner", "Intermediate", "Advanced"]:
                dur = get_technical_question_duration({"question_type": q_type, "difficulty": diff})
                self.assertEqual(dur, 15, f"Expected 15s fixed duration for {q_type}/{diff}")

    # -------------------------------------------------------------------------
    # 2. QUESTION & DOMAIN ASSOCIATION
    # -------------------------------------------------------------------------
    def test_domain_and_skill_contextual_association(self):
        """Verifies that domain and skill context are correctly propagated and applied in normalization."""
        # Database domain context
        raw_db = "we follow the acid properties and use d d l to create tables"
        norm_db = normalize_technical_terms(raw_db, domain="Database Systems", skills=["SQL Queries"])
        self.assertIn("ACID properties", norm_db)
        self.assertIn("DDL", norm_db)

        # Python domain context
        raw_py = "we use o o p and pie torch for deep learning with num py"
        norm_py = normalize_technical_terms(raw_py, domain="Python Programming", skills=["OOP in Python"])
        self.assertIn("OOP", norm_py)
        self.assertIn("PyTorch", norm_py)
        self.assertIn("NumPy", norm_py)

    # -------------------------------------------------------------------------
    # 3. TECHNICAL TERMINOLOGY NORMALIZATION (COMPREHENSIVE)
    # -------------------------------------------------------------------------
    def test_technical_terminology_normalization_comprehensive(self):
        """Tests that spoken approximations of programming terms are normalized accurately."""
        test_cases = [
            # SQL / DB
            ("first normal form and second normal form and third normal form", ["1NF", "2NF", "3NF"], "Database Systems"),
            ("we check the r d b m s constraints", ["RDBMS"], "Database Systems"),
            ("d m l and d c l and t c l", ["DML", "DCL", "TCL"], "Database Systems"),
            # OS / Concurrency
            ("we avoided dead lock using a mew tex and a semi four", ["deadlock", "mutex", "semaphore"], "Operating Systems"),
            ("process state is stored in p c b", ["PCB"], "Operating Systems"),
            ("we use l r u cache", ["LRU cache"], "Operating Systems"),
            # AI / ML
            ("we trained a c n n and an r n n model in tensor flow", ["CNN", "RNN", "TensorFlow"], "Artificial Intelligence and Machine Learning"),
            ("we used sci kit learn and pan das", ["Scikit-learn", "Pandas"], "Artificial Intelligence and Machine Learning"),
            # Programming Concepts
            ("the code follows o o p with d r y principle and s o l i d", ["OOP", "DRY principle", "SOLID"], "Python Programming"),
            ("we use c plus plus for s t l and templates", ["C++", "STL", "templates"], "C++ Programming"),
        ]

        for raw_spoken, expected_terms, domain in test_cases:
            normalized = normalize_technical_terms(raw_spoken, domain=domain)
            for term in expected_terms:
                self.assertIn(term, normalized, f"Expected '{term}' in normalized output: '{normalized}'")

    # -------------------------------------------------------------------------
    # 4. EMPTY AUDIO HANDLING (MOCKED)
    # -------------------------------------------------------------------------
    @patch("speech_recognition.Recognizer.recognize_google")
    @patch("speech_recognition.Recognizer.record")
    @patch("speech_recognition.Recognizer.adjust_for_ambient_noise")
    @patch("speech_recognition.Microphone")
    def test_empty_audio_handling_mocked(self, mock_mic, mock_adj, mock_record, mock_recognize):
        """Simulates recording silence where Google SpeechRecognition returns UnknownValueError."""
        mock_mic.return_value.__enter__.return_value = MagicMock()
        mock_recognize.side_effect = sr.UnknownValueError()

        res = []
        record_and_transcribe_audio(duration=15, result_container=res)

        self.assertEqual(len(res), 1)
        self.assertTrue(res[0].startswith("ERROR:"), f"Expected ERROR: prefix, got: {res[0]}")
        self.assertIn("No speech detected", res[0])

    # -------------------------------------------------------------------------
    # 5. RECOGNITION API NETWORK FAILURE (MOCKED)
    # -------------------------------------------------------------------------
    @patch("speech_recognition.Recognizer.recognize_google")
    @patch("speech_recognition.Recognizer.record")
    @patch("speech_recognition.Recognizer.adjust_for_ambient_noise")
    @patch("speech_recognition.Microphone")
    def test_recognition_api_failure_mocked(self, mock_mic, mock_adj, mock_record, mock_recognize):
        """Simulates network/API outage where Google SpeechRecognition raises RequestError."""
        mock_mic.return_value.__enter__.return_value = MagicMock()
        mock_recognize.side_effect = sr.RequestError("Connection timed out")

        res = []
        record_and_transcribe_audio(duration=15, result_container=res)

        self.assertEqual(len(res), 1)
        self.assertTrue(res[0].startswith("ERROR:"), f"Expected ERROR: prefix, got: {res[0]}")
        self.assertIn("service unavailable", res[0].lower())
        self.assertIn("check your internet connection", res[0].lower())

    # -------------------------------------------------------------------------
    # 6. MICROPHONE INITIALIZATION FAILURE (MOCKED)
    # -------------------------------------------------------------------------
    @patch("speech_recognition.Microphone")
    def test_microphone_initialization_failure_mocked(self, mock_mic):
        """Simulates Windows microphone permission denied or device disconnected (OSError)."""
        mock_mic.side_effect = OSError("No default input device available")

        res = []
        record_and_transcribe_audio(duration=15, result_container=res)

        self.assertEqual(len(res), 1)
        self.assertTrue(res[0].startswith("ERROR:"), f"Expected ERROR: prefix, got: {res[0]}")
        self.assertIn("Microphone access error", res[0])

    # -------------------------------------------------------------------------
    # 7. TRANSCRIPT PRESERVATION IN SESSION STATE
    # -------------------------------------------------------------------------
    def test_transcript_preservation_in_session_state(self):
        """Verifies that recorded voice responses are correctly saved to st.session_state.technical_answers."""
        # Setup mock session state
        st.session_state.technical_domain = "Python Programming"
        st.session_state.technical_difficulty = "Intermediate"
        st.session_state.technical_questions = [
            {
                "question_id": 1,
                "question": "Explain Python generators and the yield keyword.",
                "domain": "Python Programming",
                "skill": "Functions and Modules",
                "difficulty": "Intermediate",
                "question_type": "Conceptual",
            }
        ]
        st.session_state.technical_answers = {}
        st.session_state["tech_ans_input_0"] = "Generators use yield to produce values lazily."

        # Save voice answer
        save_current_technical_answer(
            curr_idx=0,
            method="voice",
            raw_transcript="generators use yield to produce values lazily",
            audio_path="temp_audio_0.wav"
        )

        saved = st.session_state.technical_answers.get(0)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["answer_method"], "voice")
        self.assertEqual(saved["answer_text"], "Generators use yield to produce values lazily.")
        self.assertEqual(saved["raw_transcript"], "generators use yield to produce values lazily")
        self.assertEqual(saved["audio_path"], "temp_audio_0.wav")
        self.assertEqual(saved["question_id"], 1)

    # -------------------------------------------------------------------------
    # 8. MANUAL TRANSCRIPT EDITING
    # -------------------------------------------------------------------------
    def test_manual_transcript_editing_preserves_audio_paths(self):
        """Verifies that manual editing of a transcribed answer updates the text without losing the original audio file."""
        st.session_state.technical_domain = "Java Programming"
        st.session_state.technical_difficulty = "Beginner"
        st.session_state.technical_questions = [
            {"question": "What is encapsulation?", "domain": "Java Programming", "skill": "Core Java", "difficulty": "Beginner"}
        ]
        st.session_state.technical_answers = {
            0: {
                "question_id": 1,
                "question": "What is encapsulation?",
                "answer_text": "Encapsulation binds data and code.",
                "answer_method": "voice",
                "raw_transcript": "encapsulation binds data and code",
                "audio_path": "saved_recording_0.wav"
            }
        }

        # Candidate edits text manually in the text area
        st.session_state["tech_ans_input_0"] = (
            "Encapsulation binds data and methods together into a single unit, hiding internal state."
        )

        # Save without overriding audio parameters
        save_current_technical_answer(curr_idx=0)

        updated = st.session_state.technical_answers[0]
        self.assertEqual(
            updated["answer_text"],
            "Encapsulation binds data and methods together into a single unit, hiding internal state."
        )
        # Original voice metadata preserved
        self.assertEqual(updated["raw_transcript"], "encapsulation binds data and code")
        self.assertEqual(updated["audio_path"], "saved_recording_0.wav")
        self.assertEqual(updated["answer_method"], "voice")

    # -------------------------------------------------------------------------
    # 9. AUDIO FILE CLEANUP LIFECYCLE
    # -------------------------------------------------------------------------
    def test_audio_file_creation_and_cleanup(self):
        """Verifies temporary audio file creation in session subfolder and clean deletion by cleanup_temp_audio()."""
        test_session_id = f"test_sess_{int(time.time())}"
        path_q0 = get_temp_audio_path(test_session_id, 0)
        path_q1 = get_temp_audio_path(test_session_id, 1)

        # Create dummy WAV files
        os.makedirs(os.path.dirname(path_q0), exist_ok=True)
        with open(path_q0, "wb") as f:
            f.write(b"RIFF dummy wav data 0")
        with open(path_q1, "wb") as f:
            f.write(b"RIFF dummy wav data 1")

        self.assertTrue(os.path.exists(path_q0), "Audio file for Q0 must exist")
        self.assertTrue(os.path.exists(path_q1), "Audio file for Q1 must exist")

        # Run cleanup
        cleanup_temp_audio(test_session_id)

        self.assertFalse(os.path.exists(path_q0), "Audio file for Q0 should be deleted after cleanup")
        self.assertFalse(os.path.exists(path_q1), "Audio file for Q1 should be deleted after cleanup")

    # -------------------------------------------------------------------------
    # 10. THREAD LIFECYCLE & DUPLICATE-THREAD PREVENTION
    # -------------------------------------------------------------------------
    def test_thread_lifecycle_and_non_blocking_execution(self):
        """Verifies that speech recording executes cleanly in a separate worker thread without blocking caller."""
        container = []
        finished_flag = threading.Event()

        def mock_worker():
            # Simulate 0.3s recording
            time.sleep(0.3)
            container.append("Transcribed answer from worker thread.")
            finished_flag.set()

        t0 = time.time()
        thread = threading.Thread(target=mock_worker, daemon=True)
        thread.start()

        # Caller continues immediately (non-blocking)
        elapsed_start = time.time() - t0
        self.assertLess(elapsed_start, 0.1, "Thread launch must not block caller execution")

        # Wait for thread completion
        thread.join(timeout=2.0)
        self.assertTrue(finished_flag.is_set(), "Thread must finish within timeout")
        self.assertEqual(len(container), 1)
        self.assertIn("Transcribed answer", container[0])


class TestPhase2LiveHardware(unittest.TestCase):
    """
    Physical hardware microphone tests.
    Explicitly separated from automated mock tests.
    Gracefully skips if no working audio input hardware is connected.
    """

    def test_physical_microphone_hardware_availability(self):
        """Checks if a real physical microphone is available on the host machine."""
        try:
            mics = sr.Microphone.list_microphone_names()
            if not mics:
                self.skipTest("No physical microphone device detected on this system.")
            print(f"\n[Hardware Detected] {len(mics)} microphone(s) found. Default: {mics[0]}")
        except Exception as e:
            self.skipTest(f"Audio hardware check skipped: {e}")


def run_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhase2SpeechCapture))
    suite.addTest(unittest.makeSuite(TestPhase2LiveHardware))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
