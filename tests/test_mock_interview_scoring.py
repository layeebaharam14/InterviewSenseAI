# -*- coding: utf-8 -*-
"""
test_mock_interview_scoring.py
Focused unit tests for Mock Interview behavioural scoring and feedback generation.

Covers:
  1. analyze_audio_behavior with valid speech
  2. analyze_audio_behavior with genuine silence
  3. analyze_audio_behavior with audio_failed=True (SR/hardware error)
  4. analyze_audio_behavior backward-compat (no audio_failed arg)
  5. calculate_scores with all valid audio+video
  6. calculate_scores with audio_failed entries (no unfair communication penalty)
  7. calculate_scores with no face detected
  8. calculate_scores empty lists
  9. Score range validation (0-100 for all metrics)
  10. generate_feedback verdict consistency
  11. generate_feedback score_note when audio unavailable
  12. generate_feedback backward-compat (no audio_questions_evaluated key)
  13. Overall score excludes communication when audio_q==0
  14. pauses default for silent recording is 0 (not duration/3)
  15. Filler word threshold triggers communication penalty correctly
  16. meaningful=False + audio_available=True triggers confidence/communication penalty
  17. meaningful=False + audio_available=False skips all audio penalties
  18. High nervousness only from video movement, not audio failures
  19. Determinism: same inputs → same outputs
  20. Full pipeline: failed-audio session produces sensible non-zero scores
"""

import unittest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interviewsense.analysis.audio_analysis import analyze_audio_behavior
from src.interviewsense.core.scoring import calculate_scores
from src.interviewsense.core.insights import generate_feedback


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_video_ok():
    """Face detected, good eye contact, low movement."""
    return {"face_detected": True, "eye_contact": "good", "movement": "low"}


def _make_video_no_face():
    """Camera present but no face detected."""
    return {"face_detected": False, "eye_contact": "poor", "movement": "high"}


def _make_audio_ok(text="I am very experienced with Python OOP concepts and have used them daily."):
    return analyze_audio_behavior(text, duration=15)


def _make_audio_silent():
    return analyze_audio_behavior("", duration=15)


def _make_audio_failed():
    return analyze_audio_behavior("", duration=15, audio_failed=True)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAudioAnalysis(unittest.TestCase):

    # 1. Valid speech
    def test_01_valid_speech(self):
        res = _make_audio_ok()
        self.assertTrue(res["audio_available"])
        self.assertTrue(res["meaningful"])
        self.assertGreater(res["word_count"], 0)
        self.assertGreater(res["words_per_minute"], 0)
        self.assertIn(res["speech_rate"], ("Slow", "Well-paced", "Fast"))
        self.assertGreaterEqual(res["fluency_score"], 0)
        self.assertLessEqual(res["fluency_score"], 100)

    # 2. Genuine silence
    def test_02_genuine_silence(self):
        res = _make_audio_silent()
        self.assertTrue(res["audio_available"])   # audio WAS captured
        self.assertFalse(res["meaningful"])
        self.assertEqual(res["word_count"], 0)
        # FIX: pauses must be 0 for silent recording, not duration/3
        self.assertEqual(res["pauses"], 0, "pauses should be 0 for silent recording")
        self.assertEqual(res["fluency_score"], 0)

    # 3. Audio pipeline failed
    def test_03_audio_pipeline_failed(self):
        res = _make_audio_failed()
        self.assertFalse(res["audio_available"])
        self.assertFalse(res["meaningful"])
        self.assertEqual(res["pauses"], 0)
        self.assertEqual(res["filler_words"], 0)

    # 4. Backward-compat: no audio_failed arg → audio_available=True
    def test_04_backward_compat_no_flag(self):
        res = analyze_audio_behavior("hello world test answer", 15)
        self.assertIn("audio_available", res)
        self.assertTrue(res["audio_available"])

    # 14. pauses=0 for silent (not duration/3)
    def test_14_pauses_zero_for_silent(self):
        for dur in (10, 15, 20, 25, 30):
            res = analyze_audio_behavior("", dur)
            self.assertEqual(res["pauses"], 0,
                             f"pauses should be 0 for silence (duration={dur})")


class TestCalculateScores(unittest.TestCase):

    # 5. All valid audio + video → reasonable scores
    def test_05_all_valid(self):
        v = [_make_video_ok()] * 5
        a = [_make_audio_ok()] * 5
        s = calculate_scores(v, a)
        self.assertEqual(s["audio_questions_evaluated"], 5)
        self.assertEqual(s["video_questions_evaluated"], 5)
        # With good video+audio, confidence should be high
        self.assertGreaterEqual(s["confidence"], 70)
        self.assertLessEqual(s["nervousness"], 30)
        self.assertGreaterEqual(s["communication"], 70)

    # 6. audio_failed entries → no communication penalty
    def test_06_audio_failed_no_communication_penalty(self):
        v = [_make_video_ok()] * 5
        a_failed = [_make_audio_failed()] * 5
        s = calculate_scores(v, a_failed)
        self.assertEqual(s["audio_questions_evaluated"], 0)
        # Communication starts at 100 and no audio penalties applied
        self.assertEqual(s["communication"], 100,
                         "communication must remain 100 when all audio failed")
        # Video was fine, so confidence should not drop from audio
        self.assertGreaterEqual(s["confidence"], 90)

    # 7. No face → nervousness high, confidence drops
    def test_07_no_face_penalties(self):
        v = [_make_video_no_face()] * 5
        a = [_make_audio_ok()] * 5
        s = calculate_scores(v, a)
        self.assertEqual(s["video_questions_evaluated"], 0)
        self.assertEqual(s["nervousness"], min(100, 50))   # 10 per question × 5
        self.assertLessEqual(s["confidence"], 70)         # starts 100 - 10×5 = 50

    # 8. Empty lists → all zeros
    def test_08_empty_lists(self):
        s = calculate_scores([], [])
        self.assertEqual(s["confidence"], 0)
        self.assertEqual(s["nervousness"], 0)
        self.assertEqual(s["communication"], 0)
        self.assertEqual(s["audio_questions_evaluated"], 0)
        self.assertEqual(s["video_questions_evaluated"], 0)

    # 9. Score range validation
    def test_09_score_range_always_0_to_100(self):
        # Extreme bad case
        v = [_make_video_no_face()] * 20
        a = [_make_audio_silent()] * 20
        s = calculate_scores(v, a)
        for key in ("confidence", "nervousness", "communication"):
            self.assertGreaterEqual(s[key], 0, f"{key} below 0")
            self.assertLessEqual(s[key], 100, f"{key} above 100")

    # 16. meaningful=False + audio_available=True → communication + confidence penalty
    def test_16_silent_available_triggers_penalties(self):
        v = [_make_video_ok()]
        a = [_make_audio_silent()]   # audio_available=True, meaningful=False
        s = calculate_scores(v, a)
        # communication should drop: meaningful penalty (-20), pauses=0 so no pause penalty
        self.assertEqual(s["communication"], 80)   # 100 - 20
        self.assertEqual(s["confidence"], 90)       # 100 - 10

    # 17. meaningful=False + audio_available=False → NO audio penalties
    def test_17_failed_audio_no_penalty(self):
        v = [_make_video_ok()]
        a = [_make_audio_failed()]   # audio_available=False
        s = calculate_scores(v, a)
        self.assertEqual(s["communication"], 100)   # no penalty
        self.assertEqual(s["confidence"], 100)       # no audio penalty

    # 18. High nervousness only from video movement, not audio failures
    def test_18_nervousness_from_video_only(self):
        # Video: high movement; Audio: failed (should not add nervousness)
        v = [{"face_detected": True, "eye_contact": "poor", "movement": "high"}]
        a = [_make_audio_failed()]
        s = calculate_scores(v, a)
        self.assertEqual(s["nervousness"], 10)   # only video movement (10)

    # 19. Determinism
    def test_19_deterministic(self):
        v = [_make_video_ok(), _make_video_no_face()]
        a = [_make_audio_ok(), _make_audio_failed()]
        s1 = calculate_scores(v, a)
        s2 = calculate_scores(v, a)
        self.assertEqual(s1, s2)

    # 20. Full pipeline: all-failed-audio session → non-zero confidence score
    def test_20_failed_audio_session_nonzero_confidence(self):
        # Simulate 5 questions with good camera but failed audio (the original bug scenario)
        v = [_make_video_ok()] * 5
        a = [_make_audio_failed()] * 5
        s = calculate_scores(v, a)
        fb = generate_feedback(s)
        # Confidence should NOT be 0 (was the original bug)
        self.assertGreater(s["confidence"], 50,
                           "Confidence must not collapse to 0 from audio failures alone")
        # Communication must NOT be 0 either
        self.assertEqual(s["communication"], 100,
                         "Communication must not be penalised when audio pipeline failed")
        # Overall score should be reasonable
        self.assertGreater(fb["overall_score"], 50)


class TestGenerateFeedback(unittest.TestCase):

    def _base_scores(self, **overrides):
        s = {
            "confidence": 80,
            "nervousness": 20,
            "communication": 80,
            "audio_questions_evaluated": 5,
            "video_questions_evaluated": 5,
        }
        s.update(overrides)
        return s

    # 10. Verdict consistency
    def test_10_verdict_ready_for_high_scores(self):
        fb = generate_feedback(self._base_scores(confidence=90, nervousness=10, communication=90))
        self.assertEqual(fb["verdict"], "Ready for Interview")
        self.assertGreaterEqual(fb["overall_score"], 80)

    def test_10b_verdict_not_ready_for_low_scores(self):
        fb = generate_feedback(self._base_scores(confidence=20, nervousness=80, communication=20))
        self.assertEqual(fb["verdict"], "Not Ready")

    def test_10c_verdict_needs_improvement(self):
        fb = generate_feedback(self._base_scores(confidence=60, nervousness=40, communication=60))
        self.assertIn(fb["verdict"], ("Needs Improvement", "Ready for Interview"))

    # 11. score_note present when audio_q==0
    def test_11_score_note_when_no_audio(self):
        fb = generate_feedback(self._base_scores(audio_questions_evaluated=0))
        self.assertIn("score_note", fb)
        self.assertGreater(len(fb["score_note"]), 0,
                           "score_note should explain communication exclusion")

    # 12. Backward-compat: no audio_questions_evaluated key
    def test_12_backward_compat_no_audio_key(self):
        scores_legacy = {"confidence": 70, "nervousness": 30, "communication": 70}
        fb = generate_feedback(scores_legacy)
        self.assertIn("verdict", fb)
        self.assertIn("overall_score", fb)
        self.assertGreaterEqual(fb["overall_score"], 0)
        self.assertLessEqual(fb["overall_score"], 100)

    # 13. Overall score excludes communication when audio_q==0
    def test_13_overall_score_excludes_comm_when_no_audio(self):
        s = self._base_scores(
            confidence=80, nervousness=20, communication=0,
            audio_questions_evaluated=0
        )
        fb = generate_feedback(s)
        # score = (80 + (100-20)) / 2 = (80+80)/2 = 80
        self.assertAlmostEqual(fb["overall_score"], 80, delta=1)

    # Feedback sections are always populated
    def test_feedback_sections_non_empty(self):
        for conf in (90, 60, 30):
            for nerv in (10, 40, 70):
                s = self._base_scores(confidence=conf, nervousness=nerv)
                fb = generate_feedback(s)
                self.assertTrue(len(fb["positive"]) > 0, "positive must not be empty")
                self.assertTrue(len(fb["improvement"]) > 0, "improvement must not be empty")

    # 15. Filler word threshold triggers communication penalty
    def test_15_filler_word_threshold(self):
        # 4 filler words: > 3 → penalty
        text_fillers = "um um um um I think Python is good"
        res = analyze_audio_behavior(text_fillers, 15)
        self.assertGreaterEqual(res["filler_words"], 4)
        v = [_make_video_ok()]
        a = [res]
        s = calculate_scores(v, a)
        # communication penalty: -5 for fillers
        self.assertLessEqual(s["communication"], 95)


if __name__ == "__main__":
    unittest.main(verbosity=2)
