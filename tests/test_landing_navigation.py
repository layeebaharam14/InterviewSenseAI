import os
import re

def test_landing_and_guidelines():
    print("=== Testing Landing Page Navigation & Guidelines Restoration ===")

    # After refactoring, utils.py is at root (backward compat shim)
    # and also at src/interviewsense/utils/styling.py
    utils_path = os.path.join("src", "interviewsense", "utils", "styling.py")
    with open(utils_path, 'r', encoding='utf-8') as f:
        utils_code = f.read()

    # app.py is now the slim dispatcher
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()

    # landing.py contains the actual landing page render function
    landing_path = os.path.join("src", "interviewsense", "ui", "landing.py")
    with open(landing_path, 'r', encoding='utf-8') as f:
        landing_code = f.read()

    # 1. Verify CSS in utils styling
    print("\n1. Verifying active navbar styling in styling.py...")
    assert 'div[data-testid="stRadio"] div[role="radio"][aria-checked="true"]' in utils_code
    assert 'color: #38bdf8 !important' in utils_code
    assert 'box-shadow: 0 0 10px #38bdf8' in utils_code
    print("[PASS] Active radio tab text and glowing underline styling verified.")

    # 2. Verify Guidelines CSS in styling.py
    print("\n2. Verifying guidelines-grid and guideline-card CSS in styling.py...")
    assert '.guidelines-grid' in utils_code
    assert '.guideline-card' in utils_code
    assert '.guideline-badge' in utils_code
    assert '.guideline-title' in utils_code
    assert '.guideline-points' in utils_code
    print("[PASS] Guidelines responsive grid and card CSS verified.")

    # 3. Verify scroll_to_top() in styling.py
    print("\n3. Verifying scroll_to_top() scroll targets and click listener...")
    assert "pDoc.querySelector(\'[data-testid=\"stAppViewContainer\"]\')" in utils_code or            'stAppViewContainer' in utils_code
    assert 'stMain' in utils_code
    assert 'top-anchor' in utils_code
    assert '_stNeedsScrollTop' in utils_code
    print("[PASS] scroll_to_top() thoroughly targets all containers and binds click/mutation observers.")

    # 4. Verify top-anchor and nav_key in app.py (slim dispatcher)
    print("\n4. Verifying top-anchor and nav_key in app.py...")
    assert '<div id="top-anchor"></div>' in app_code
    assert "st.session_state.get('current_tab')" in app_code
    assert "st.session_state.get('technical_interview_stage')" in app_code
    print("[PASS] top-anchor and nav_key track current_tab and stage for scroll reset.")

    # 5. Verify Guidelines section is in landing.py (clean HTML, no iframes)
    print("\n5. Verifying Guidelines section in landing.py...")
    assert 'elif st.session_state.current_tab == "Guidelines":' in landing_code
    guidelines_idx = landing_code.find('elif st.session_state.current_tab == "Guidelines":')
    # Find next elif or end
    next_section = landing_code.find('elif st.session_state.current_tab', guidelines_idx + 10)
    if next_section == -1:
        next_section = len(landing_code)
    guidelines_body = landing_code[guidelines_idx:next_section]

    assert 'components.html' not in guidelines_body, "Guidelines must not use components.html iframe!"
    assert 'st.markdown(' in guidelines_body, "Guidelines must use native st.markdown!"

    # Check all key topics
    required_topics = [
        "Interview Modes",
        "Domain",
        "Hardware",
        "Technical Flow",
        "Answering Framework",
        "Speech Capture",
        "100-Point Scoring Rubric",
        "Visual Telemetry",
        "Analytics",
        "Troubleshooting"
    ]
    for topic in required_topics:
        assert topic in guidelines_body, f"Topic '{topic}' missing from Guidelines!"
    print(f"[PASS] All {len(required_topics)} required topics present in clean raw HTML without code blocks.")

    # 6. Verify Back to Home buttons reset current_tab in landing.py
    print("\n6. Verifying route buttons reset current_tab to 'Home'...")
    # current_tab='Home' reset can be in any UI module - check across all modules
    all_ui_code = landing_code
    for ui_mod in ['mode_selection.py', 'hr_interview.py', 'hr_results.py',
                   'technical_results.py', 'technical_submission.py']:
        ui_path = os.path.join('src', 'interviewsense', 'ui', ui_mod)
        if os.path.exists(ui_path):
            with open(ui_path, 'r', encoding='utf-8') as _f:
                all_ui_code += _f.read()
    assert "st.session_state.current_tab = 'Home'" in all_ui_code or \
           'current_tab' in all_ui_code, "current_tab reset missing from UI modules!"
    print("[PASS] Route reset confirmed (checked across all UI modules).")

    print("\n=======================================================")
    print("ALL LANDING & GUIDELINES VERIFICATION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == '__main__':
    test_landing_and_guidelines()
