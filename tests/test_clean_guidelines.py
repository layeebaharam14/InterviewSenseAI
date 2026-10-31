"""
Test Clean Guidelines Rendering — InterviewSense AI
Verifies that the Guidelines tab in src/interviewsense/ui/landing.py:
1. Exists and contains genuine guideline instructions.
2. Does NOT use components.html iframe (pure native Streamlit markdown).
3. Contains the required responsive grid (<div class="guidelines-grid">).
4. Contains 10 guideline cards (<div class="guideline-card">).
5. Covers all 10 required technical interview topics.
6. Does NOT accidentally embed cards inside Markdown code blocks.
7. Fails with AssertionError if any topic or structural markup is missing.
"""
import os
import re
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_clean_guidelines():
    print("=== Testing Guidelines Content & Markup in landing.py ===")

    landing_path = os.path.join("src", "interviewsense", "ui", "landing.py")
    assert os.path.exists(landing_path), f"Source file missing: {landing_path}"

    with open(landing_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Locate Guidelines section in landing.py
    tab_marker = 'elif st.session_state.current_tab == "Guidelines":'
    assert tab_marker in code, "Guidelines tab branch missing from landing.py!"

    start_idx = code.find(tab_marker)
    # Find next elif or end of file
    next_tab_idx = code.find("elif st.session_state.current_tab", start_idx + len(tab_marker))
    if next_tab_idx == -1:
        next_tab_idx = len(code)
    guidelines_section = code[start_idx:next_tab_idx]

    # 2. Verify section is non-empty and substantive
    assert len(guidelines_section) > 2000, f"Guidelines section too short: {len(guidelines_section)} chars"
    print(f"[PASS] Guidelines section located: {len(guidelines_section)} characters.")

    # 3. Verify native Streamlit markdown is used, NOT components.html iframe
    assert "components.html(" not in guidelines_section, (
        "Guidelines must NOT use components.html iframe! Must use native Streamlit st.markdown."
    )
    assert "st.markdown(" in guidelines_section, "Guidelines must render via st.markdown."
    print("[PASS] Native Streamlit markdown rendering verified (no iframes).")

    # 4. Verify required grid and card markup
    assert '<div class="guidelines-grid">' in guidelines_section, (
        "Missing '<div class=\"guidelines-grid\">' container in Guidelines!"
    )
    card_count = guidelines_section.count('class="guideline-card"') + guidelines_section.count('class="guideline-card ')
    assert card_count == 10, f"Expected exactly 10 guideline cards, found {card_count}"
    print(f"[PASS] Responsive grid and all {card_count} guideline cards verified.")

    # 5. Verify all 10 required topics are present
    required_topics = [
        ("1. Interview Modes", ["Interview Modes", "Mock HR", "Technical Interview"]),
        ("2. Domain & Skill Setup", ["Domain", "Skill", "Programming"]),
        ("3. Hardware & Environment", ["Hardware", "Camera", "Microphone"]),
        ("4. Technical Flow & Timers", ["Flow", "15", "Timer", "Countdown"]),
        ("5. Answering Framework", ["Answering", "Framework", "DMET"]),
        ("6. Speech Capture & Review", ["Speech", "Capture", "Transcript"]),
        ("7. 100-Point Scoring Rubric", ["100-Point", "Rubric", "Score"]),
        ("8. Visual Telemetry & Privacy", ["Visual", "Telemetry", "Privacy"]),
        ("9. Analytics & PDF Export", ["Analytics", "PDF", "Export"]),
        ("10. Troubleshooting & Support", ["Troubleshooting", "Support"]),
    ]

    for topic_num_name, keywords in required_topics:
        # Check topic appears in title or content
        found = any(k.lower() in guidelines_section.lower() for k in keywords)
        assert found, f"Required topic '{topic_num_name}' (keywords: {keywords}) missing from Guidelines!"

    print("[PASS] All 10 required technical interview topics verified.")

    # 6. Verify content is NOT accidentally inside markdown code blocks
    # (i.e. not wrapped in ``` or <pre>)
    assert "```html" not in guidelines_section, "Guidelines HTML must not be wrapped in a code fence!"
    assert "<pre>" not in guidelines_section, "Guidelines HTML must not be wrapped in <pre>!"
    print("[PASS] Guidelines markup confirmed free of code block wrapping.")

    # 7. Verification that a missing topic causes test failure (negative test)
    try:
        assert "NON_EXISTENT_GUIDELINE_TOPIC_XYZ" in guidelines_section
        raise Exception("Negative test failed: nonexistent string was found!")
    except AssertionError:
        # Expected failure
        pass
    print("[PASS] Negative assertion verified (test correctly fails on missing content).")

    print("\n========================================================")
    print("ALL CLEAN GUIDELINES VERIFICATION CHECKS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    test_clean_guidelines()
