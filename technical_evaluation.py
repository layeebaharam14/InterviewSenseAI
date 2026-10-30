"""
technical_evaluation.py
Structured Technical Answer Evaluation Engine for InterviewSense AI.
Evaluates technical answers using multi-criteria weighted scoring:
- Technical Correctness (Weight: 40)
- Conceptual Understanding (Weight: 25)
- Relevance (Weight: 15)
- Completeness (Weight: 15)
- Explanation Quality (Weight: 5)
Total: 100 points.

Architecture: Rule-based semantic baseline with synonym mapping, concept coverage analysis,
misconception detection, and structured feedback generation. Designed for future LLM API drop-in.
"""

import re
from typing import Dict, Any, List, Tuple

# Common stop words to exclude during relevance tokenization
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "don", "should", "now",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "having", "do", "does", "did", "doing", "what", "which", "who", "whom",
    "this", "that", "these", "those", "am", "it", "its", "how", "why", "explain",
    "describe", "difference", "compare", "briefly", "code", "write", "example"
}

# Technical synonyms and alternative phrasings
SYNONYM_MAP = {
    "mro": ["method resolution order", "c3 linearization", "inheritance order", "resolution order"],
    "gil": ["global interpreter lock", "interpreter lock", "thread lock", "cpython lock"],
    "oop": ["object oriented programming", "object-oriented", "classes and objects"],
    "mutable": ["modifiable", "changeable", "in-place modification", "can be changed", "altered"],
    "immutable": ["unmodifiable", "unchangeable", "cannot be changed", "read only", "constant"],
    "acid": ["atomicity consistency isolation durability", "transactional properties", "db transactions"],
    "tcp": ["transmission control protocol", "connection oriented", "three-way handshake", "reliable delivery"],
    "udp": ["user datagram protocol", "connectionless", "datagram", "unreliable delivery"],
    "bfs": ["breadth first search", "queue based", "level order"],
    "dfs": ["depth first search", "stack based", "recursive traversal"],
    "sql": ["structured query language", "relational queries", "rdbms queries"],
    "nosql": ["not only sql", "non-relational", "document store", "key-value store"],
    "orm": ["object relational mapping", "hibernate", "sqlalchemy", "entity framework"],
    "rest": ["representational state transfer", "restful", "http verbs", "stateless api"],
    "api": ["application programming interface", "endpoints", "web service"],
    "polymorphism": ["multiple forms", "dynamic binding", "method overriding", "duck typing"],
    "inheritance": ["subclassing", "derived class", "parent child class", "extends"],
    "encapsulation": ["data hiding", "information hiding", "private variables", "getters and setters"],
    "abstraction": ["abstract classes", "interfaces", "hiding implementation details"],
    "gc": ["garbage collection", "memory deallocation", "reference counting", "cyclic gc"],
    "time complexity": ["big o", "runtime", "asymptotic complexity", "o(n)", "o(1)", "o(log n)"],
    "space complexity": ["memory complexity", "auxiliary space", "memory usage"],
    "primary key": ["unique identifier", "non-null key", "unique key"],
    "foreign key": ["referential integrity", "references parent table", "cross-table relation"],
    "indexing": ["b-tree", "hash index", "query optimization", "fast lookup"],
    "normalization": ["1nf", "2nf", "3nf", "bcnf", "reducing redundancy", "data integrity"],
    "deadlock": ["mutual exclusion", "hold and wait", "no preemption", "circular wait"],
    "concurrency": ["multithreading", "asynchronous", "parallel execution", "thread safety"],
    "stack": ["lifo", "last in first out", "call stack"],
    "queue": ["fifo", "first in first out"],
}

def clean_and_tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words excluding common stopwords."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]

def match_concept_in_text(concept: str, text: str) -> Tuple[bool, bool]:
    """
    Checks if a concept appears in text, and whether it appears in a negated context.
    Returns (is_present: bool, is_negated: bool).
    """
    c_lower = concept.lower().strip()
    t_lower = text.lower()

    # Collect variants
    variants = [c_lower]
    for key, syns in SYNONYM_MAP.items():
        if key in c_lower or any(s in c_lower for s in syns):
            variants.extend(syns)
            variants.append(key)

    is_found = False
    found_var = None

    for var in set(variants):
        if var in t_lower:
            is_found = True
            found_var = var
            break
        pattern = r"\b" + re.escape(var) + r"\b"
        if re.search(pattern, t_lower):
            is_found = True
            found_var = var
            break

    if not is_found:
        concept_tokens = clean_and_tokenize(c_lower)
        if len(concept_tokens) >= 2 and all(token in t_lower for token in concept_tokens):
            is_found = True
            found_var = concept_tokens[0]

    if not is_found:
        return False, False

    # Check if negated in the sentence
    is_negated = False
    negation_regex = r"\b(not|never|no|don't|do not|doesn't|does not|without|cannot|can't)\b(?:\s+\w+){0,4}\s+" + re.escape(found_var)
    if re.search(negation_regex, t_lower):
        is_negated = True

    return True, is_negated

def calculate_relevance(question_data: dict, answer_text: str) -> Tuple[float, List[str]]:
    """
    Calculates relevance of the answer to the question (Max 15 points).
    Checks overlap with question prompt, domain, and skill.
    """
    q_text = question_data.get("question", "")
    domain = question_data.get("domain", "")
    skill = question_data.get("skill", "")

    q_tokens = set(clean_and_tokenize(q_text + " " + skill + " " + domain))
    ans_tokens = set(clean_and_tokenize(answer_text))

    if not ans_tokens:
        return 0.0, []

    # Calculate token overlap
    overlap = q_tokens.intersection(ans_tokens)
    overlap_ratio = len(overlap) / max(len(q_tokens), 1)

    # Check domain/skill presence
    domain_tokens = set(clean_and_tokenize(domain))
    skill_tokens = set(clean_and_tokenize(skill))
    domain_match = bool(domain_tokens.intersection(ans_tokens))
    skill_match = bool(skill_tokens.intersection(ans_tokens))

    # Base score
    if overlap_ratio >= 0.35 or (domain_match and skill_match and len(overlap) >= 2):
        score = 15.0
    elif overlap_ratio >= 0.20 or len(overlap) >= 3:
        score = 12.0
    elif overlap_ratio >= 0.10 or len(overlap) >= 2:
        score = 9.0
    elif len(overlap) >= 1:
        score = 5.0
    else:
        # Check if any key concept is present
        key_concepts = question_data.get("key_concepts", [])
        if any(match_concept_in_text(c, answer_text)[0] for c in key_concepts):
            score = 6.0
        else:
            score = 0.0

    return min(15.0, round(score, 1)), list(overlap)

def detect_misconceptions(common_mistakes: List[str], answer_text: str) -> List[str]:
    """Identifies detectable technical misconceptions from common mistakes."""
    detected = []
    t_lower = answer_text.lower()
    for mistake in common_mistakes:
        m_lower = mistake.lower()
        keywords = clean_and_tokenize(m_lower)
        if len(keywords) >= 2 and all(k in t_lower for k in keywords[:2]):
            detected.append(mistake)
    return detected

def evaluate_technical_answer(question_data: Dict[str, Any], answer_text: str) -> Dict[str, Any]:
    """
    Evaluates a single technical candidate answer against question rubrics and criteria.

    Returns a structured dictionary with:
    - score: Overall score out of 100
    - criteria_scores: Breakdown for Technical Correctness (40), Conceptual Understanding (25),
      Relevance (15), Completeness (15), Explanation Quality (5)
    - what_you_did_well: List of concepts explained correctly
    - missing_points: List of important concepts omitted
    - areas_to_improve: Concrete actionable suggestions
    - suggested_answer: Model answer for the question
    - final_evaluation: Summary verdict
    """
    clean_ans = str(answer_text).strip() if answer_text else ""
    q_text = question_data.get("question", "Technical Question")
    domain = question_data.get("domain", "General Tech")
    skill = question_data.get("skill", "General")
    difficulty = question_data.get("difficulty", "Intermediate")
    q_type = question_data.get("question_type", "Conceptual")
    expected_ans = question_data.get("expected_answer", "Refer to standard documentation for technical specifics.")
    key_concepts = question_data.get("key_concepts", [skill, domain])
    important_points = question_data.get("important_points", [f"Core mechanics of {skill}"])
    common_mistakes = question_data.get("common_mistakes", ["Providing vague or generic statements without technical detail."])

    # 1. Blank Answer Handling
    if not clean_ans:
        return {
            "score": 0,
            "criteria_scores": {
                "technical_correctness": 0,
                "conceptual_understanding": 0,
                "relevance": 0,
                "completeness": 0,
                "explanation_quality": 0
            },
            "what_you_did_well": [],
            "missing_points": important_points if important_points else key_concepts,
            "areas_to_improve": [
                "No response was provided. Take time to formulate a technical answer explaining core definitions, key components, and examples."
            ],
            "suggested_answer": expected_ans,
            "final_evaluation": "Unanswered: No response provided. Full marks omitted.",
            "is_unanswered": True,
            "question": q_text,
            "domain": domain,
            "skill": skill,
            "difficulty": difficulty,
            "question_type": q_type,
            "candidate_answer": ""
        }

    # 2. Relevance Scoring (Max 15)
    rel_score, overlap_tokens = calculate_relevance(question_data, clean_ans)

    # If completely irrelevant, heavily penalize and return early with low score (<= 10)
    if rel_score <= 1.0:
        return {
            "score": 5,
            "criteria_scores": {
                "technical_correctness": 2,
                "conceptual_understanding": 1,
                "relevance": 1,
                "completeness": 1,
                "explanation_quality": 0
            },
            "what_you_did_well": [],
            "missing_points": important_points,
            "areas_to_improve": [
                "The response is off-topic or does not address the technical subject asked. Focus strictly on the question's domain and keywords."
            ],
            "suggested_answer": expected_ans,
            "final_evaluation": "Irrelevant response: The answer does not address the question asked.",
            "is_unanswered": False,
            "question": q_text,
            "domain": domain,
            "skill": skill,
            "difficulty": difficulty,
            "question_type": q_type,
            "candidate_answer": clean_ans
        }

    # 3. Conceptual Understanding (Max 25) & What You Did Well
    matched_concepts = []
    negated_concepts = []
    unmatched_concepts = []

    for concept in key_concepts:
        present, negated = match_concept_in_text(concept, clean_ans)
        if present:
            if negated:
                negated_concepts.append(concept)
            else:
                matched_concepts.append(concept)
        else:
            unmatched_concepts.append(concept)

    concept_ratio = len(matched_concepts) / max(len(key_concepts), 1)
    
    # Check depth of explanation
    ans_word_count = len(clean_ans.split())
    depth_multiplier = min(1.0, ans_word_count / 25.0)

    conceptual_score = round(concept_ratio * 25.0 * (0.7 + 0.3 * depth_multiplier), 1)
    # Deduct for falsely negated concepts
    if negated_concepts:
        conceptual_score = max(0.0, conceptual_score - len(negated_concepts) * 5.0)
    conceptual_score = min(25.0, max(2.0 if matched_concepts else 0.0, conceptual_score))

    # 4. Completeness (Max 15) & Missing Points
    matched_points = []
    missing_points = []

    for pt in important_points:
        pt_tokens = clean_and_tokenize(pt)
        token_hits = sum(1 for tok in pt_tokens if tok in clean_ans.lower())
        if token_hits >= max(1, len(pt_tokens) // 2) or match_concept_in_text(pt[:30], clean_ans)[0]:
            matched_points.append(pt)
        else:
            missing_points.append(pt)

    completeness_ratio = len(matched_points) / max(len(important_points), 1)
    completeness_score = round(completeness_ratio * 15.0, 1)

    # 5. Technical Correctness (Max 40)
    mistakes_detected = detect_misconceptions(common_mistakes, clean_ans)
    
    # Baseline correctness from concept ratio and point coverage
    base_correctness = (concept_ratio * 0.6 + completeness_ratio * 0.4) * 40.0

    # Boost correctness if candidate used code or precise terminology
    if "`" in clean_ans or "def " in clean_ans or "class " in clean_ans or "SELECT" in clean_ans.upper():
        base_correctness = min(40.0, base_correctness + 3.0)

    # Penalty for detected misconceptions and falsely negated concepts
    mistake_penalty = (len(mistakes_detected) * 10.0) + (len(negated_concepts) * 12.0)
    correctness_score = max(0.0, round(base_correctness - mistake_penalty, 1))
    correctness_score = min(40.0, correctness_score)

    # If the response is largely incorrect or full of misconceptions, cap total score
    is_largely_incorrect = (len(negated_concepts) > 0 or len(mistakes_detected) > 0) and concept_ratio < 0.35

    # 6. Explanation Quality (Max 5)
    quality_score = 1.0
    if ans_word_count >= 15:
        quality_score += 1.5
    if ans_word_count >= 35:
        quality_score += 1.0
    if any(p in clean_ans for p in [".", ";", "\n", ":"]):
        quality_score += 1.0
    if len(clean_ans.split()) >= 60 and ("because" in clean_ans.lower() or "for example" in clean_ans.lower() or "such as" in clean_ans.lower()):
        quality_score += 0.5
    quality_score = min(5.0, round(quality_score, 1))

    # 7. Aggregate Total Score
    total_score = round(correctness_score + conceptual_score + rel_score + completeness_score + quality_score)
    if is_largely_incorrect:
        total_score = min(35, total_score)
    total_score = max(5, min(100, int(total_score)))

    # Adjust feedback lists
    what_well = [f"Correctly explained or referenced '{c}'" for c in matched_concepts]
    if matched_points and len(what_well) < 3:
        what_well.extend([f"Addressed key aspect: {p}" for p in matched_points[:2]])
    if not what_well:
        what_well.append("Attempted to address the question with general technical context.")

    # Formulate actionable areas to improve
    areas_to_improve = []
    if negated_concepts:
        for nc in negated_concepts:
            areas_to_improve.append(f"Clarify usage: '{nc}' is required or supported in this context, not rejected.")
    if unmatched_concepts:
        areas_to_improve.append(f"Strengthen your explanation by discussing: {', '.join(unmatched_concepts[:3])}.")
    if mistakes_detected:
        for m in mistakes_detected:
            areas_to_improve.append(f"Review misconception: {m}.")
    if ans_word_count < 30:
        areas_to_improve.append("Elaborate further with practical examples, edge cases, or trade-offs to demonstrate deeper technical mastery.")
    if not areas_to_improve:
        areas_to_improve.append("Good coverage! Consider including concrete syntax examples or real-world production performance trade-offs.")

    # Final summary verdict
    if total_score >= 90:
        final_eval = "Outstanding answer! Demonstrates deep conceptual understanding, accurate terminology, and comprehensive technical detail."
    elif total_score >= 75:
        final_eval = "Very good response. Covers the primary mechanics and definitions accurately with minor opportunities for additional depth."
    elif total_score >= 60:
        final_eval = "Satisfactory answer. Displays foundational understanding of core concepts but misses a few key technical nuances."
    elif total_score >= 40:
        final_eval = "Partially correct. Identified some relevant aspects, but lacks sufficient technical precision and completeness."
    else:
        final_eval = "Needs improvement. The response is either too brief, conceptually incomplete, or contains notable inaccuracies."

    return {
        "score": total_score,
        "criteria_scores": {
            "technical_correctness": round(correctness_score, 1),
            "conceptual_understanding": round(conceptual_score, 1),
            "relevance": round(rel_score, 1),
            "completeness": round(completeness_score, 1),
            "explanation_quality": round(quality_score, 1)
        },
        "what_you_did_well": what_well,
        "missing_points": missing_points if missing_points else ["All major reference points were addressed."],
        "areas_to_improve": areas_to_improve,
        "suggested_answer": expected_ans,
        "final_evaluation": final_eval,
        "is_unanswered": False,
        "question": q_text,
        "domain": domain,
        "skill": skill,
        "difficulty": difficulty,
        "question_type": q_type,
        "candidate_answer": clean_ans
    }

def classify_performance(score: float) -> str:
    """Classifies interview score into one of five performance levels."""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Poor"

def evaluate_technical_interview(technical_questions: List[Dict[str, Any]], technical_answers: Dict[int, Any]) -> Dict[str, Any]:
    """
    Evaluates all submitted answers for a technical interview in order.

    Returns:
    - evaluations: List of evaluation result dicts for each question
    - overall_score: Weighted interview score (0-100)
    - average_score: Average score across all questions (including unanswered as 0)
    - performance_level: Classification level string
    - total_questions: Total question count
    - answered_questions: Answered question count
    - unanswered_questions: Unanswered question count
    - strongest_skill: Highest performing skill (name, avg_score)
    - weakest_skill: Lowest performing skill (name, avg_score)
    - skill_averages: Dictionary of skill -> average score
    """
    evaluations: List[Dict[str, Any]] = []
    total_q = len(technical_questions)

    if total_q == 0:
        return {
            "evaluations": [],
            "overall_score": 0,
            "average_score": 0.0,
            "performance_level": "Poor",
            "total_questions": 0,
            "answered_questions": 0,
            "unanswered_questions": 0,
            "strongest_skill": "N/A",
            "weakest_skill": "N/A",
            "skill_averages": {}
        }

    # Evaluate in exact order
    for idx, q_data in enumerate(technical_questions):
        ans_entry = technical_answers.get(idx, {})
        if isinstance(ans_entry, dict):
            ans_text = ans_entry.get("answer_text", "")
        else:
            ans_text = str(ans_entry) if ans_entry else ""

        eval_res = evaluate_technical_answer(q_data, ans_text)
        eval_res["question_index"] = idx
        eval_res["question_number"] = idx + 1
        evaluations.append(eval_res)

    # Compute scores (unanswered questions naturally score 0)
    scores = [e["score"] for e in evaluations]
    answered_count = sum(1 for e in evaluations if not e.get("is_unanswered", False))
    unanswered_count = total_q - answered_count
    
    average_score = round(sum(scores) / total_q, 1) if total_q > 0 else 0.0
    overall_score = int(round(average_score))
    performance_level = classify_performance(overall_score)

    # Group scores by skill
    skill_scores: Dict[str, List[float]] = {}
    for e in evaluations:
        sk = e.get("skill", "General")
        skill_scores.setdefault(sk, []).append(e["score"])

    skill_averages = {
        sk: round(sum(sc_list) / len(sc_list), 1)
        for sk, sc_list in skill_scores.items()
    }

    # Identify strongest and weakest skills
    if skill_averages:
        sorted_skills = sorted(skill_averages.items(), key=lambda item: item[1], reverse=True)
        strongest_skill = f"{sorted_skills[0][0]} ({sorted_skills[0][1]}/100)"
        weakest_skill = f"{sorted_skills[-1][0]} ({sorted_skills[-1][1]}/100)"
    else:
        strongest_skill = "N/A"
        weakest_skill = "N/A"

    return {
        "evaluations": evaluations,
        "overall_score": overall_score,
        "average_score": average_score,
        "performance_level": performance_level,
        "total_questions": total_q,
        "answered_questions": answered_count,
        "unanswered_questions": unanswered_count,
        "strongest_skill": strongest_skill,
        "weakest_skill": weakest_skill,
        "skill_averages": skill_averages
    }
