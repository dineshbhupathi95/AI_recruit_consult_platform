"""Analyze resume timelines vs job experience requirements."""

import re
from datetime import datetime
from typing import Any

_PRESENT_TOKENS = frozenset({"present", "current", "now", "ongoing"})


def _parse_year_month(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None
    cleaned = value.strip().lower()
    if cleaned in _PRESENT_TOKENS:
        now = datetime.now()
        return now.year, now.month

    year_match = re.search(r"(20\d{2}|19\d{2})", cleaned)
    if not year_match:
        return None, None
    year = int(year_match.group(1))

    month_match = re.search(r"(?<![\d])(0?[1-9]|1[0-2])(?![\d])", cleaned)
    if month_match and int(month_match.group(1)) <= 12:
        return year, int(month_match.group(1))

    month_names = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    for name, month_num in month_names.items():
        if name in cleaned:
            return year, month_num

    return year, 1


def _months_between(start_year: int, start_month: int, end_year: int, end_month: int) -> int:
    return max(0, (end_year - start_year) * 12 + (end_month - start_month))


def calculate_total_experience_years(experience: list[dict[str, Any]]) -> float:
    total_months = 0
    for entry in experience:
        start_year, start_month = _parse_year_month(entry.get("start_date"))
        if entry.get("is_current"):
            end_year, end_month = _parse_year_month("present")
        else:
            end_year, end_month = _parse_year_month(entry.get("end_date"))
        if start_year and end_year and start_month and end_month:
            total_months += _months_between(start_year, start_month, end_year, end_month)
    return round(total_months / 12, 1)


def find_timeline_gaps(
    education: list[dict[str, Any]],
    experience: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []

    grad_years: list[int] = []
    edu_start_years: list[int] = []
    for edu in education:
        grad_year, _ = _parse_year_month(edu.get("graduation_year"))
        start_year, _ = _parse_year_month(edu.get("start_year") or edu.get("graduation_year"))
        if grad_year:
            grad_years.append(grad_year)
        if start_year:
            edu_start_years.append(start_year)

    if experience:
        for idx, exp in enumerate(experience):
            start_year, start_month = _parse_year_month(exp.get("start_date"))
            if exp.get("is_current"):
                end_year, end_month = _parse_year_month("present")
            else:
                end_year, end_month = _parse_year_month(exp.get("end_date"))
            if not start_year or not end_year:
                continue

            if idx + 1 < len(experience):
                next_start_year, next_start_month = _parse_year_month(experience[idx + 1].get("start_date"))
                if next_start_year and next_start_month:
                    gap_months = _months_between(
                        next_start_year, next_start_month, end_year, end_month
                    )
                    if gap_months >= 3:
                        gaps.append({
                            "label": f"Between {exp.get('company', 'role')} and next role",
                            "from_date": f"{next_start_year:04d}-{next_start_month:02d}",
                            "to_date": f"{end_year:04d}-{end_month:02d}",
                            "months": gap_months,
                            "suggestion": (
                                "Add a contract, freelance, or training entry for this period, "
                                "or align dates with recruiter-approved adjustments."
                            ),
                        })

        first_exp = experience[0]
        first_start_year, first_start_month = _parse_year_month(first_exp.get("start_date"))
        if grad_years and first_start_year and first_start_month:
            latest_grad = max(grad_years)
            grad_month = 6
            gap_months = _months_between(latest_grad, grad_month, first_start_year, first_start_month)
            if gap_months >= 6:
                gaps.append({
                    "label": "Education to first full-time role",
                    "from_date": f"{latest_grad:04d}-{grad_month:02d}",
                    "to_date": f"{first_start_year:04d}-{first_start_month:02d}",
                    "months": gap_months,
                    "suggestion": (
                        "Fill with internship, trainee role, or education projects; "
                        "or extend education timeline (start year / projects during study)."
                    ),
                })

    return gaps


def build_recommendations(
    candidate_years: float,
    job_min_years: int | None,
    gaps: list[dict[str, Any]],
) -> list[str]:
    recommendations: list[str] = []
    if job_min_years is not None and candidate_years < job_min_years:
        shortfall = round(job_min_years - candidate_years, 1)
        recommendations.append(
            f"Job requires ~{job_min_years} years; parsed resume shows ~{candidate_years} years "
            f"({shortfall} year shortfall)."
        )
        recommendations.append(
            "Choose a gap strategy: extend education/projects, add internship/training entry, "
            "or emphasize depth without inflating dates."
        )
    if gaps:
        recommendations.append(
            f"Found {len(gaps)} timeline gap(s). Review dates or add entries before building."
        )
    if not recommendations:
        recommendations.append("Experience aligns with job requirements. Review fields and build.")
    return recommendations


GAP_STRATEGY_OPTIONS = [
    {
        "id": "none",
        "label": "Standard build",
        "description": "Optimize content for the JD without changing employment dates.",
    },
    {
        "id": "extend_education",
        "label": "Extend education timeline",
        "description": (
            "Use education start year and academic projects to cover time before the first job "
            "(e.g. projects during degree, not new employers)."
        ),
    },
    {
        "id": "add_training_entry",
        "label": "Add internship / training entry",
        "description": (
            "Insert an internship, trainee, or freelance role between education and first company "
            "using the fields below."
        ),
    },
    {
        "id": "emphasize_strengths",
        "label": "Emphasize strengths (honest)",
        "description": (
            "Do not inflate years. Strengthen summary and recent achievements for senior-level depth."
        ),
    },
    {
        "id": "recruiter_manual",
        "label": "Use recruiter dates only",
        "description": "Build strictly from the experience and education you enter below — no AI date changes.",
    },
]


def analyze_resume_for_job(
    parsed_resume: dict[str, Any],
    job_min_years: int | None,
    job_max_years: int | None,
) -> dict[str, Any]:
    experience = parsed_resume.get("experience") or []
    education = parsed_resume.get("education") or []
    candidate_years = calculate_total_experience_years(experience)
    gaps = find_timeline_gaps(education, experience)

    experience_gap_years: float | None = None
    if job_min_years is not None:
        experience_gap_years = round(max(0.0, job_min_years - candidate_years), 1)

    return {
        "job_experience_min_years": job_min_years,
        "job_experience_max_years": job_max_years,
        "candidate_total_experience_years": candidate_years,
        "experience_shortfall_years": experience_gap_years,
        "timeline_gaps": gaps,
        "gap_strategy_options": GAP_STRATEGY_OPTIONS,
        "recommendations": build_recommendations(candidate_years, job_min_years, gaps),
    }
