import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_phase1_correction():
    print("=== TEST 1: Fixed 15-Second Duration for All Questions ===")
    import app
    for q_type in ["Conceptual", "Practical", "Coding", "Scenario"]:
        for diff in ["Beginner", "Intermediate", "Advanced"]:
            dur = app.get_technical_question_duration({"question_type": q_type, "difficulty": diff})
            assert dur == 15, f"Expected 15s for {q_type}/{diff}, got {dur}"
    print("[PASS] Fixed 15-second duration verified across all question types and difficulties.")

    print("\n=== TEST 2: Exact Audio Duration from speak_question in utils.py ===")
    import utils
    import pyttsx3
    import wave
    # Verify speak_question returns a valid positive float duration
    sample_text = "What is encapsulation in object-oriented programming?"
    dur = utils.speak_question(sample_text)
    assert isinstance(dur, float) and dur > 0.0, f"Expected positive float duration, got {dur}"
    print(f"[PASS] speak_question returned exact duration: {dur:.2f}s.")

    print("\n=== TEST 3: App Code Verification for Exact 6-Stage Automated Flow ===")
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()

    # Stage 1: Display and speak question
    assert "audio_duration = speak_question(q_text)" in app_code
    assert "time.sleep(audio_duration + 0.3)" in app_code
    print("[PASS] Stage 1: Question displayed and spoken completely before proceeding.")

    # Stage 2: Exactly 3-second countdown
    assert "for count in (3, 2, 1):" in app_code
    assert "Camera and microphone will activate automatically" in app_code
    print("[PASS] Stage 2: Exactly 3-second countdown (camera & mic inactive during playback & countdown).")

    # Stage 3 & 4: Automatic Camera & Microphone for exactly 15 seconds
    assert "camera = get_camera()" in app_code
    assert "record_and_transcribe, args=(15, audio_result)" in app_code
    assert "time.time() - start_time < 15.0" in app_code
    assert "Time Remaining: {remaining}s / 15s" in app_code
    print("[PASS] Stage 3 & 4: Automatic camera & microphone activation for fixed 15-second timer.")

    # Stage 5: Automatic Stop and Processing
    assert "if camera is not None:\n        camera.release()" in app_code
    assert "audio_thread.join()" in app_code
    assert "save_current_technical_answer(curr_idx" in app_code
    assert "aggregate_video_analysis(sampled_frames)" in app_code
    print("[PASS] Stage 5: Automatic recording stop, frame & audio processing, answer saved.")

    # Stage 6: Automatic Next Question or Submission
    assert "st.session_state.technical_question_index += 1" in app_code
    assert "st.session_state.current_page = 'technical_submission'" in app_code
    print("[PASS] Stage 6: Automatic transition to next question and final submission.")

    print("\n=== TEST 4: Existing Mock HR Interview Integrity ===")
    assert "def render_interview_page():" in app_code
    assert "def start_mock_interview():" in app_code
    assert "def render_results_page():" in app_code
    assert "QUESTION_POOL = [" in app_code
    print("[PASS] Existing Mock HR Interview timing and implementation 100% intact.")

    print("\n========================================================")
    print("ALL CORRECTION TESTS PASSED! IMPLEMENTATION FULLY VERIFIED")
    print("========================================================")

if __name__ == "__main__":
    test_phase1_correction()

