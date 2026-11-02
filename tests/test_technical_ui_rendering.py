"""
Test Technical Interview UI Rendering & Read-Only Results Verification
Checks:
1. Technical Submission Summary does not render as raw HTML/code blocks.
2. Question-by-question summary in Results is read-only (no st.text_area / st.text_input in Tab 5).
3. Candidate answers are displayed as styled read-only text with HTML escaping.
4. Score cards, radial gauge, and all 5 tabs in Technical Results render with zero <pre><code> code blocks.
5. Submission review screen preserves its editing and re-transcription controls.
"""
import os
import sys
import re
import markdown_it

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interviewsense.utils.styling import clean_html


def test_submission_ui_rendering():
    print("=== Testing Technical Submission UI Rendering ===")
    sub_path = os.path.join("src", "interviewsense", "ui", "technical_submission.py")
    assert os.path.exists(sub_path), f"File missing: {sub_path}"

    with open(sub_path, "r", encoding="utf-8") as f:
        code = f.read()

    md = markdown_it.MarkdownIt()

    # 1. Check all st.markdown calls in submission page
    st_md_blocks = list(re.finditer(r'st\.markdown\(\s*(?:f?["\']{3})(.*?)(?:["\']{3})', code, re.DOTALL))
    for m in st_md_blocks:
        block = m.group(1)
        rendered = md.render(block)
        assert "<pre>" not in rendered and "<code>" not in rendered, (
            f"st.markdown block in technical_submission.py produces <pre><code>: {block[:60]}"
        )

    # 2. Check render_html calls in submission page
    render_blocks = list(re.finditer(r'render_html\(\s*(?:f?["\']{3})(.*?)(?:["\']{3})', code, re.DOTALL))
    assert len(render_blocks) >= 2, "Expected render_html calls for submission summary and badges"
    for m in render_blocks:
        block = m.group(1)
        cleaned = clean_html(block)
        rendered = md.render(cleaned)
        assert "<pre>" not in rendered and "<code>" not in rendered, (
            f"render_html block in technical_submission.py produces <pre><code>: {block[:60]}"
        )

    # 3. Confirm editing controls REMAIN in technical_submission.py
    assert "st.text_area(" in code, "Editable text area must be preserved in technical_submission.py!"
    assert "Save Q" in code or "btn_save_edit" in code, "Save answer button must be preserved in technical_submission.py!"
    assert "retranscribe" in code.lower(), "Audio re-transcription feature must be preserved in technical_submission.py!"
    print("[PASS] Technical Submission screen verified: clean rendering + editing controls intact.")


def test_results_ui_rendering():
    print("=== Testing Technical Results UI Rendering & Read-Only Controls ===")
    res_path = os.path.join("src", "interviewsense", "ui", "technical_results.py")
    assert os.path.exists(res_path), f"File missing: {res_path}"

    with open(res_path, "r", encoding="utf-8") as f:
        code = f.read()

    md = markdown_it.MarkdownIt()

    # 1. Check all st.markdown calls in results page
    st_md_blocks = list(re.finditer(r'st\.markdown\(\s*(?:f?["\']{3})(.*?)(?:["\']{3})', code, re.DOTALL))
    for m in st_md_blocks:
        block = m.group(1)
        rendered = md.render(block)
        assert "<pre>" not in rendered and "<code>" not in rendered, (
            f"st.markdown block in technical_results.py produces <pre><code>: {block[:60]}"
        )

    # 2. Check render_html calls in results page
    render_blocks = list(re.finditer(r'render_html\(\s*(?:f?["\']{3})(.*?)(?:["\']{3})', code, re.DOTALL))
    assert len(render_blocks) >= 10, f"Expected at least 10 render_html blocks, found {len(render_blocks)}"
    for m in render_blocks:
        block = m.group(1)
        cleaned = clean_html(block)
        rendered = md.render(cleaned)
        assert "<pre>" not in rendered and "<code>" not in rendered, (
            f"render_html block in technical_results.py produces <pre><code>: {block[:60]}"
        )

    # 3. Confirm NO editable controls in question-wise summary in Tab 5
    # Find Tab 5 section:
    tab5_marker = "with tab_questions:"
    assert tab5_marker in code, "tab_questions not found in technical_results.py"
    tab5_start = code.find(tab5_marker)
    tab5_end = code.find("# SECTION C:", tab5_start)
    if tab5_end == -1:
        tab5_end = len(code)
    tab5_code = code[tab5_start:tab5_end]

    assert "st.text_area(" not in tab5_code, "Editable st.text_area found in Results Tab 5!"
    assert "st.text_input(" not in tab5_code, "Editable st.text_input found in Results Tab 5!"
    assert "html.escape(" in tab5_code, "Candidate answer and model answer in Tab 5 must be HTML escaped!"
    print("[PASS] Results Tab 5 is strictly read-only with properly escaped candidate response.")

    # 4. Check that all 5 tabs exist and are present in st.tabs
    for tab_name in [
        "Combined Summary & Roadmap",
        "Technical Performance",
        "Speech & Communication",
        "Facial & Visual Behaviour",
        "Question-Wise Detailed Analysis"
    ]:
        assert tab_name in code, f"Tab {tab_name} missing from technical_results.py"

    print("[PASS] All 5 Results tabs verified with zero raw code blocks.")




def test_technical_setup_ui():
    print("=== Testing Technical Setup UI Elements & Validation ===")
    setup_path = os.path.join("src", "interviewsense", "ui", "technical_setup.py")
    assert os.path.exists(setup_path), f"File missing: {setup_path}"

    with open(setup_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. No empty setup-card boxes or unwanted st.write("---") lines
    assert '<div class="setup-card">' not in code, "Unclosed setup-card class found creating empty boxes!"
    assert 'st.write("---")' not in code, "Unwanted horizontal divider lines st.write('---') found!"

    # 2. Native container border card used
    assert "with st.container(border=True):" in code, "st.container(border=True) missing from setup page!"

    # 3. Default dropdown placeholders
    assert 'placeholder="Select your domain"' in code, "Placeholder 'Select your domain' missing!"
    assert 'placeholder="Select interview difficulty"' in code, "Placeholder 'Select interview difficulty' missing!"
    assert 'placeholder="Select number of questions"' in code, "Placeholder 'Select number of questions' missing!"

    # 4. Question count includes 3 Questions
    assert '"3 Questions"' in code, "'3 Questions' option missing from question count options!"

    # 5. Validation blocks if missing required selections
    assert "if not st.session_state.technical_domain:" in code, "Domain validation missing!"
    assert "elif not st.session_state.technical_skills:" in code, "Skills validation missing!"
    assert "elif not st.session_state.technical_difficulty:" in code, "Difficulty validation missing!"
    assert "elif not st.session_state.technical_num_questions:" in code, "Question count validation missing!"

    # 6. Navigation buttons
    assert "← Back to Modes" in code, "Back to Modes button missing!"
    assert "Back to Home" in code, "Back to Home button missing!"

    # 7. Page guard and scroll reset
    assert "if st.session_state.get('current_page') != 'technical_setup':" in code, "Setup page guard missing!"
    assert "scroll_to_top()" in code, "scroll_to_top() call missing on setup generation!"

    print("[PASS] Technical Setup UI verified: placeholders, containers, validation, and navigation intact.")


def test_question_generation_3_questions():
    print("=== Testing 3 Questions Generation & Duplicate Avoidance ===")
    from src.interviewsense.data.technical_questions import generate_technical_questions

    qs = generate_technical_questions(
        domain="Python",
        skills=["Syntax & Basics", "Data Structures"],
        difficulty="Beginner",
        num_questions=3
    )

    assert len(qs) == 3, f"Expected 3 questions, got {len(qs)}"
    q_texts = [q["question"] for q in qs]
    assert len(set(q_texts)) == 3, f"Duplicate questions found in 3-question set: {q_texts}"
    print(f"[PASS] Successfully generated exactly {len(qs)} distinct questions with zero duplicates.")


def test_live_interview_stability_and_audio():
    print("=== Testing Live Interview Layout Stability & Audio Single-Playback ===")
    interview_path = os.path.join("src", "interviewsense", "ui", "technical_interview.py")
    assert os.path.exists(interview_path), f"File missing: {interview_path}"

    with open(interview_path, "r", encoding="utf-8") as f:
        int_code = f.read()

    # 1. Page guard to completely hide setup form during interview
    assert "if st.session_state.get('current_page') != 'technical_interview':" in int_code, "Interview page guard missing!"

    # 2. Camera preview centered
    assert "st.columns([1, 6, 1])" in int_code, "Centered camera columns [1, 6, 1] missing!"

    # 3. Camera standby box to prevent vertical layout jump
    assert "camera-standby-box" in int_code, "camera-standby-box placeholder missing!"

    # 4. Spoken flag marked before audio call to prevent duplicate triggering
    spoken_flag_pos = int_code.find("st.session_state[spoken_key] = True")
    speak_call_pos = int_code.find("speak_question(q_text)")
    assert spoken_flag_pos != -1 and speak_call_pos != -1, "Audio playback logic missing!"
    assert spoken_flag_pos < speak_call_pos, "spoken_key must be marked True BEFORE calling speak_question!"

    # 5. Styling.py audio purge & single-playback guard
    styling_path = os.path.join("src", "interviewsense", "utils", "styling.py")
    with open(styling_path, "r", encoding="utf-8") as f:
        style_code = f.read()

    assert "winsound.SND_PURGE" in style_code, "winsound audio purge missing from speak_question!"
    assert "if not played_via_winsound:" in style_code, "Double-playback guard missing from speak_question!"
    assert "camera-standby-box" in style_code, "camera-standby-box CSS missing from styling.py!"
    assert 'div[data-testid="stVerticalBlockBorderWrapper"]' in style_code, "Container card CSS missing!"

    print("[PASS] Live Interview layout stability, centering, and single audio playback verified.")


if __name__ == "__main__":
    test_submission_ui_rendering()
    test_results_ui_rendering()
    test_technical_setup_ui()
    test_question_generation_3_questions()
    test_live_interview_stability_and_audio()
    print("\nALL TECHNICAL UI & WORKFLOW TESTS PASSED 100%!")

