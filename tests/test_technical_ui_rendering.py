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


if __name__ == "__main__":
    test_submission_ui_rendering()
    test_results_ui_rendering()
    print("\nALL TECHNICAL UI RENDERING TESTS PASSED SUCCESSFULLY!")

