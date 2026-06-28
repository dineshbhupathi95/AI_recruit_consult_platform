"""Structured screening interview plan."""

from typing import Any

# 15 MCQ + 2 scenario + 1 coding
INTERVIEW_QUESTION_TYPES: list[str] = ["mcq"] * 15 + ["scenario"] * 2 + ["coding"] * 1
TOTAL_INTERVIEW_QUESTIONS = len(INTERVIEW_QUESTION_TYPES)

PHASE_LABELS = {
    "mcq": "Multiple Choice",
    "scenario": "Scenario Based",
    "coding": "Coding Challenge",
}


def question_type_for_index(index: int) -> str:
    if index < 0 or index >= TOTAL_INTERVIEW_QUESTIONS:
        return "mcq"
    return INTERVIEW_QUESTION_TYPES[index]


def phase_label_for_type(question_type: str) -> str:
    return PHASE_LABELS.get(question_type, question_type)


def build_question_response_payload(
    question_data: dict[str, Any],
    question_number: int,
    interview_status: Any,
) -> dict[str, Any]:
    q_type = question_type_for_index(question_number - 1)
    return {
        "question": str(question_data.get("question", "")),
        "interview_status": interview_status,
        "question_number": question_number,
        "question_type": q_type,
        "options": question_data.get("options", []) if q_type == "mcq" else [],
        "phase_label": phase_label_for_type(q_type),
        "total_questions": TOTAL_INTERVIEW_QUESTIONS,
        "is_complete": False,
    }
