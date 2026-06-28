"""Mock AI provider for tests and local development without API keys."""

from typing import Any

from app.providers.base import AIProvider


class MockAIProvider(AIProvider):
    """Deterministic fake AI responses for integration tests."""

    async def parse_resume(self, resume_text: str) -> dict[str, Any]:
        return {
            "basic_details": {
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1-555-0100",
                "location": "San Francisco, CA",
            },
            "summary": "Experienced software engineer with Python and FastAPI expertise.",
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "TechCorp",
                    "start_date": "2020-01",
                    "end_date": "present",
                    "bullets": ["Built scalable APIs", "Led team of 5 engineers"],
                }
            ],
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "institution": "State University",
                    "graduation_year": "2018",
                }
            ],
            "raw_text_length": len(resume_text),
        }

    async def build_resume(
        self,
        candidate_profile: dict[str, Any],
        parsed_resume: dict[str, Any],
        job_description: str,
        recruiter_notes: str | None = None,
        build_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        name = f"{candidate_profile.get('first_name', '')} {candidate_profile.get('last_name', '')}".strip()
        result = {
            "basic_details": {
                "full_name": name or parsed_resume.get("basic_details", {}).get("full_name", "Candidate"),
                "email": candidate_profile.get("email") or parsed_resume.get("basic_details", {}).get("email"),
                "phone": candidate_profile.get("phone"),
            },
            "summary": parsed_resume.get("summary", "Professional summary tailored to role."),
            "experience": parsed_resume.get("experience", []),
            "skills": parsed_resume.get("skills", []),
            "education": parsed_resume.get("education", []),
            "target_job": job_description[:200],
            "recruiter_notes": recruiter_notes,
            "gap_strategy": (build_context or {}).get("gap_strategy"),
        }
        return result

    async def convert_upload_to_jinja_template(
        self,
        source_html: str | None,
        parsed_resume: dict[str, Any],
    ) -> dict[str, Any]:
        from app.utils.resume_template_upload import fallback_jinja_from_parsed

        html_template, css_styles = fallback_jinja_from_parsed(parsed_resume)
        return {"html_template": html_template, "css_styles": css_styles}

    async def score_resume(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> dict[str, Any]:
        skills = resume_json.get("skills", [])
        matched = [s for s in required_skills if s in skills]
        return {
            "overall_score": 82.5,
            "keyword_match": 78.0,
            "skill_match": 85.0,
            "experience_match": 80.0,
            "semantic_similarity": 75.0,
            "formatting": 90.0,
            "grammar": 88.0,
            "achievements": 80.0,
            "missing_keywords": [s for s in required_skills if s not in skills],
            "suggestions": ["Add more quantified achievements"],
            "improvement_areas": ["Leadership examples"],
        }

    async def generate_interview_question(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        previous_questions: list[str],
        previous_answers: list[str],
        question_type: str = "mcq",
        question_number: int = 1,
    ) -> dict[str, Any]:
        if question_type == "mcq":
            return {
                "question": f"MCQ {question_number}: Which best describes REST API design principles?",
                "options": [
                    {"id": "a", "text": "Stateless communication with clear resource URLs"},
                    {"id": "b", "text": "Persistent server-side sessions for every request"},
                    {"id": "c", "text": "Binary-only payloads without HTTP verbs"},
                    {"id": "d", "text": "Single endpoint for all operations"},
                ],
            }
        if question_type == "scenario":
            return {
                "question": f"Scenario {question_number - 15}: Describe how you would debug a production API latency spike.",
                "options": [],
            }
        return {
            "question": "Coding: Write a function to find the two numbers in an array that sum to a target value.",
            "options": [],
        }

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        resume_json: dict[str, Any],
        job_description: str,
    ) -> dict[str, Any]:
        return {"score": 8.0, "feedback": "Good answer with relevant examples."}

    async def summarize_interview(
        self,
        transcript: list[dict[str, str]],
        resume_json: dict[str, Any],
        job_description: str,
        coding_evaluations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "summary": "Candidate demonstrated strong technical skills and clear communication.",
            "technical_score": 8.5,
            "coding_score": None,
            "communication_score": 8.0,
            "confidence_score": 7.5,
            "problem_solving_score": 8.0,
            "recommendation": "hire",
            "strengths": ["Python expertise", "API design"],
            "weaknesses": ["Limited cloud experience"],
        }
