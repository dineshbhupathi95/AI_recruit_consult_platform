"""Unit tests for resume timeline analysis."""

from app.services.resume_timeline_analysis import (
    analyze_resume_for_job,
    calculate_total_experience_years,
    find_timeline_gaps,
)


def test_calculate_total_experience_years() -> None:
    experience = [
        {"company": "A", "title": "Dev", "start_date": "2018", "end_date": "2020", "is_current": False},
        {"company": "B", "title": "Sr Dev", "start_date": "2020", "end_date": "Present", "is_current": True},
    ]
    years = calculate_total_experience_years(experience)
    assert years >= 6.0


def test_education_to_first_job_gap() -> None:
    education = [{"institution": "Uni", "degree": "BS", "graduation_year": "2015"}]
    experience = [
        {"company": "Corp", "title": "Dev", "start_date": "2018-01", "end_date": "Present", "is_current": True},
    ]
    gaps = find_timeline_gaps(education, experience)
    assert any("Education to first" in g["label"] for g in gaps)


def test_analyze_shortfall() -> None:
    parsed = {
        "experience": [
            {"company": "A", "title": "Dev", "start_date": "2020", "end_date": "Present", "is_current": True},
        ],
        "education": [{"institution": "Uni", "degree": "BS", "graduation_year": "2019"}],
    }
    result = analyze_resume_for_job(parsed, job_min_years=7, job_max_years=10)
    assert result["candidate_total_experience_years"] < 7
    assert result["experience_shortfall_years"] is not None
    assert result["experience_shortfall_years"] > 0
    assert len(result["recommendations"]) > 0
