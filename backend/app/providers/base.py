"""Abstract AI provider interface for recruitment workflows."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Switchable AI backend (OpenAI, Azure, DeepSeek, etc.)."""

    @abstractmethod
    async def parse_resume(self, resume_text: str) -> dict[str, Any]:
        """Extract structured resume data from plain text."""

    @abstractmethod
    async def build_resume(
        self,
        candidate_profile: dict[str, Any],
        parsed_resume: dict[str, Any],
        job_description: str,
        recruiter_notes: str | None = None,
        build_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate ATS-optimized resume JSON for a job."""

    @abstractmethod
    async def score_resume(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> dict[str, Any]:
        """Calculate ATS-style resume score against a job."""

    @abstractmethod
    async def generate_interview_question(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        previous_questions: list[str],
        previous_answers: list[str],
        question_type: str = "mcq",
        question_number: int = 1,
    ) -> dict[str, Any]:
        """Generate structured interview question (mcq, scenario, or coding)."""

    @abstractmethod
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        resume_json: dict[str, Any],
        job_description: str,
    ) -> dict[str, Any]:
        """Evaluate a single interview answer."""

    @abstractmethod
    async def summarize_interview(
        self,
        transcript: list[dict[str, str]],
        resume_json: dict[str, Any],
        job_description: str,
        coding_evaluations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Produce interview summary and recommendation."""

    @abstractmethod
    async def convert_upload_to_jinja_template(
        self,
        source_html: str | None,
        parsed_resume: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert uploaded resume HTML + parsed data into Jinja2 template parts."""
