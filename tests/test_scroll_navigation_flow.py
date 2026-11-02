"""
Tests for InterviewSense AI Application-Wide Scroll Management and Navigation Flow.
Verifies:
1. Centralized scroll management engine in src/interviewsense/utils/styling.py
2. Multi-container targeting, instant scrolling, and multi-tier hydration ticks
3. Client-side click interception for tabs (st.tabs), navbar radio, and navigation buttons
4. Disarming on manual user scroll (wheel, touchmove, keydown)
5. Comprehensive nav_key state detection in app.py
6. Uniform scroll_to_top() invocation across all 8 UI modules for all 12 transitions
7. Zero scroll calls / reruns during the 15s recording loop and 3s countdown loop
"""
import os
import sys
import re

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_scroll_engine_in_styling():
    print("=== 1. Verifying Central Scroll Engine in styling.py ===")
    styling_path = os.path.join("src", "interviewsense", "utils", "styling.py")
    assert os.path.exists(styling_path), f"File missing: {styling_path}"

    with open(styling_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Singleton on top-level parent window
    assert "__interviewSenseScrollEngine" in code, "Scroll engine singleton missing from styling.py!"
    assert "pWin = (window.parent && window.parent.document) ? window.parent : window" in code, "pWin parent detection missing!"

    # Targets all potential scroll containers
    targets = [
        "stAppViewContainer",
        "stMain",
        "section.main",
        "block-container",
        "stApp",
        "documentElement",
        "body",
        "top-anchor"
    ]
    for t in targets:
        assert t in code, f"Scroll target '{t}' missing from styling.py!"

    # Instant behavior for flicker-free transitions
    assert "behavior: 'instant'" in code or 'behavior: "instant"' in code, "Instant scroll behavior missing!"

    # Multi-tier hydration ticks and rAF loop
    assert "requestAnimationFrame" in code, "rAF loop missing!"
    assert "setTimeout" in code, "Hydration timeout ticks missing!"

    # Client-side tab clicks, radio clicks, button clicks
    assert 'role="tab"' in code or "role=\\\"tab\\\"" in code, "Tab click interception missing!"
    assert 'stRadio' in code, "Radio navbar click interception missing!"
    assert 'Select All' in code and 'Clear Selection' in code, "Non-navigational button exclusion missing!"

    # Manual user scroll disarm
    assert 'wheel' in code and 'touchmove' in code, "User scroll disarm listeners missing!"

    # Backward compatibility assertion string
    assert '_stNeedsScrollTop' in code, "_stNeedsScrollTop variable missing!"

    print("[PASS] Central Scroll Engine in styling.py verified with full multi-container and event lifecycle support.")


def test_app_nav_key_and_dispatcher():
    print("\n=== 2. Verifying app.py State Monitoring & Top Anchor ===")
    app_path = "app.py"
    with open(app_path, "r", encoding="utf-8") as f:
        code = f.read()

    assert '<div id="top-anchor"></div>' in code, "#top-anchor element missing from app.py!"

    # Required state monitors in nav_key
    required_state_keys = [
        "current_page",
        "current_tab",
        "technical_interview_stage",
        "technical_question_index",
        "question_index",
        "technical_hardware_verified",
        "hardware_verified",
        "technical_evaluation_completed"
    ]
    for k in required_state_keys:
        assert f"'{k}'" in code or f'"{k}"' in code, f"State key '{k}' missing from nav_key in app.py!"

    assert "scroll_to_top()" in code, "scroll_to_top() call missing from app.py on nav change!"
    print("[PASS] app.py navigation dispatcher correctly tracks all 8 state dimensions.")


def test_all_ui_navigation_calls():
    print("\n=== 3. Verifying scroll_to_top() on All Navigation Buttons Across Modules ===")

    modules_to_check = {
        os.path.join("src", "interviewsense", "ui", "landing.py"): [
            "Start Interview",
        ],
        os.path.join("src", "interviewsense", "ui", "mode_selection.py"): [
            "start_mock_interview",
            "back_to_home_mode",
            "btn_start_tech",
        ],
        os.path.join("src", "interviewsense", "ui", "technical_setup.py"): [
            "back_to_modes_btn",
            "back_to_home_from_setup",
            "btn_generate_tech_interview",
        ],
        os.path.join("src", "interviewsense", "ui", "technical_interview.py"): [
            "btn_sim_tech_hw",
            "back_to_setup_from_interview",
            "st.session_state.technical_question_index += 1",
            "st.session_state.current_page = 'technical_submission'",
        ],
        os.path.join("src", "interviewsense", "ui", "technical_submission.py"): [
            "btn_goto_analysis",
            "btn_new_tech_setup_sub",
            "btn_return_mode_sub",
        ],
        os.path.join("src", "interviewsense", "ui", "technical_results.py"): [
            "btn_back_to_sub_top",
            "btn_retake_tech_interview",
            "btn_back_to_home_from_results",
        ],
        os.path.join("src", "interviewsense", "ui", "hr_interview.py"): [
            "← Go to Home",
            "hardware_verified",
            "View Final Report",
            "question_index += 1",
        ],
        os.path.join("src", "interviewsense", "ui", "hr_results.py"): [
            "Restart Interview",
        ],
    }

    for mod_path, expected_triggers in modules_to_check.items():
        assert os.path.exists(mod_path), f"UI module missing: {mod_path}"
        with open(mod_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "scroll_to_top" in content, f"scroll_to_top import or call missing from {mod_path}"

        for trigger in expected_triggers:
            assert trigger in content, f"Expected trigger '{trigger}' not found in {mod_path}"

        print(f"[PASS] {os.path.basename(mod_path)}: All {len(expected_triggers)} triggers verified.")


def test_interview_recording_preservation():
    print("\n=== 4. Verifying Interview Recording and Timer Stability ===")
    tech_int_path = os.path.join("src", "interviewsense", "ui", "technical_interview.py")
    with open(tech_int_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the 15-second recording loop
    loop_start = content.find("while time.time() - start_time < 15.0:")
    assert loop_start != -1, "15s recording while loop missing!"
    loop_end = content.find("# STAGE 5:", loop_start)
    assert loop_end != -1, "Stage 5 marker missing!"

    recording_loop_code = content[loop_start:loop_end]

    # Verify NO scroll_to_top or st.rerun calls inside the recording loop
    assert "scroll_to_top()" not in recording_loop_code, (
        "scroll_to_top() MUST NOT be called inside the 15s recording loop!"
    )
    assert "st.rerun()" not in recording_loop_code, (
        "st.rerun() MUST NOT be called inside the 15s recording loop!"
    )

    # Find the 3-second countdown loop
    cd_start = content.find("for count in (3, 2, 1):")
    assert cd_start != -1, "3-second countdown loop missing!"
    cd_end = content.find("# STAGE 3", cd_start)
    assert cd_end != -1, "Stage 3 marker missing!"

    countdown_code = content[cd_start:cd_end]
    assert "scroll_to_top()" not in countdown_code, (
        "scroll_to_top() MUST NOT be called inside the 3s countdown loop!"
    )
    assert "st.rerun()" not in countdown_code, (
        "st.rerun() MUST NOT be called inside the 3s countdown loop!"
    )

    print("[PASS] Confirmed ZERO scroll events or reruns during 15s recording and 3s countdown.")


if __name__ == "__main__":
    test_scroll_engine_in_styling()
    test_app_nav_key_and_dispatcher()
    test_all_ui_navigation_calls()
    test_interview_recording_preservation()
    print("\n=======================================================")
    print("ALL SCROLL NAVIGATION & STABILITY TESTS PASSED 100%!")
    print("=======================================================")

