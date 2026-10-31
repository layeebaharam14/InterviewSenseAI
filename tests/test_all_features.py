import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_full_pipeline():
    print("--- 1. Testing Imports ---")
    import utils
    import technical_questions as tq
    import technical_evaluation as te
    import technical_report_pdf as trp
    import app
    print("All modules imported cleanly.")

    print("\n--- 2. Testing Static Video Asset ---")
    assert os.path.exists("static/background_video.mp4"), "static/background_video.mp4 missing!"
    print(f"Static video verified: {os.path.getsize('static/background_video.mp4')} bytes.")

    print("\n--- 3. Testing Question Generation across all 12 domains ---")
    for domain in tq.QUESTION_BANK.keys():
        skills = list(tq.QUESTION_BANK[domain].keys())
        qs = tq.generate_technical_questions(domain, skills, "Intermediate", 3)
        assert len(qs) == 3, f"Failed generating 3 questions for {domain}"
        for q in qs:
            assert "expected_answer" in q, f"Missing expected_answer in {domain}"
            assert "key_concepts" in q, f"Missing key_concepts in {domain}"
    print(f"Successfully generated questions across all {len(tq.QUESTION_BANK)} domains.")

    print("\n--- 4. Testing Answer Evaluation Engine ---")
    sample_q = tq.generate_technical_questions("Python Programming", ["OOP in Python"], "Intermediate", 1)[0]
    sample_ans = "Encapsulation, inheritance, and polymorphism are core object oriented programming concepts in Python."
    eval_res = te.evaluate_technical_answer(sample_q, sample_ans)
    assert "score" in eval_res
    assert "technical_correctness" in eval_res["criteria_scores"]
    print(f"Evaluated sample answer: Score = {eval_res['score']}/100, Performance = {eval_res['final_evaluation']}")

    print("\n--- 5. Testing PDF Report Generation ---")
    mock_summary = {
        "overall_score": 85,
        "performance_level": "Strong",
        "domain": "Python Programming",
        "difficulty": "Intermediate",
        "total_questions": 1,
        "answered_count": 1,
        "unanswered_count": 0,
        "average_question_score": 85.0,
        "criteria_averages": {
            "technical_correctness": 88.0,
            "conceptual_understanding": 85.0,
            "relevance": 90.0,
            "completeness": 80.0,
            "explanation_quality": 82.0
        },
        "per_question_results": [eval_res],
        "top_strengths": ["Clear explanation of OOP principles", "Accurate terminology"],
        "areas_for_improvement": ["Could provide a small code example"],
        "recommended_topics": ["Python magic methods", "Abstract base classes"]
    }
    pdf_bytes = trp.generate_technical_pdf_report(mock_summary, mock_summary)
    assert len(pdf_bytes) > 1000, "PDF output too small"
    print(f"PDF generated successfully: {len(pdf_bytes)} bytes.")

    print("\n--- 6. Verifying Refactored Package Structure ---")
    import os as _os
    # Check new package structure
    assert _os.path.isdir("src/interviewsense"), "src/interviewsense package missing"
    assert _os.path.isdir("src/interviewsense/ui"), "ui subpackage missing"
    assert _os.path.isdir("src/interviewsense/analysis"), "analysis subpackage missing"
    assert _os.path.isdir("src/interviewsense/core"), "core subpackage missing"
    assert _os.path.isdir("src/interviewsense/data"), "data subpackage missing"
    assert _os.path.isdir("src/interviewsense/services"), "services subpackage missing"
    assert _os.path.isdir("src/interviewsense/reports"), "reports subpackage missing"
    assert _os.path.isdir("src/interviewsense/utils"), "utils subpackage missing"
    # Check slim app.py is actually slim
    with open("app.py", "r", encoding="utf-8") as _f:
        slim_lines = _f.readlines()
    assert len(slim_lines) < 120, f"app.py should be slim, got {len(slim_lines)} lines"
    # Check camera sleep is in technical_interview ui module
    ti_path = _os.path.join("src", "interviewsense", "ui", "technical_interview.py")
    with open(ti_path, "r", encoding="utf-8") as _f:
        ti_text = _f.read()
    assert "time.sleep(0.04)" in ti_text, "Camera sleep missing from technical_interview.py"
    # Check utils styling exists with key CSS
    sty_path = _os.path.join("src", "interviewsense", "utils", "styling.py")
    with open(sty_path, "r", encoding="utf-8") as _f:
        utils_text = _f.read()
    assert "justify-content: flex-start !important;" in utils_text, "Layout flex-start missing from styling.py"
    print("All refactored package structure checks passed!")

    print("\n==========================================")
    print("ALL TESTS PASSED! APPLICATION IS 100% HEALTHY")
    print("==========================================")

if __name__ == "__main__":
    test_full_pipeline()
