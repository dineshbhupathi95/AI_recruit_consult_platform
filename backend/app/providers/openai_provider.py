"""OpenAI-compatible AI provider."""

import json
import re
from typing import Any

import httpx

from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.prompts.interview import (
    EVALUATE_ANSWER_PROMPT,
    GENERATE_CODING_PROMPT,
    GENERATE_MCQ_PROMPT,
    GENERATE_SCENARIO_PROMPT,
    SUMMARIZE_INTERVIEW_PROMPT,
)
from app.prompts.resume import (
    BUILD_RESUME_PROMPT,
    CONVERT_UPLOAD_TEMPLATE_PROMPT,
    PARSE_RESUME_PROMPT,
    SCORE_RESUME_PROMPT,
)
from app.providers.base import AIProvider

logger = get_logger(__name__)


def _parse_json_content(content: str) -> dict[str, Any]:
    """Parse JSON from model output (handles markdown fences from local models)."""
    text = content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValidationError("AI response was not valid JSON. Try a larger model or use Mock provider.")


class OpenAIProvider(AIProvider):
    """OpenAI Chat Completions provider (also Azure OpenAI & compatible APIs)."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout: float = 120.0,
        azure_api_version: str | None = None,
        use_api_key_header: bool = False,
        require_auth: bool = True,
        use_json_response_format: bool = True,
    ) -> None:
        if require_auth and not api_key:
            raise ValidationError("AI API key is not configured")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._azure_api_version = azure_api_version
        self._use_api_key_header = use_api_key_header
        self._require_auth = require_auth
        self._use_json_response_format = use_json_response_format

    def _chat_url(self) -> str:
        if self._azure_api_version:
            return f"{self._base_url}/chat/completions?api-version={self._azure_api_version}"
        return f"{self._base_url}/chat/completions"

    def _request_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if not self._require_auth:
            return headers
        if self._use_api_key_header:
            headers["api-key"] = self._api_key
        else:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _chat_json(self, system: str, user: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        if self._use_json_response_format:
            payload["response_format"] = {"type": "json_object"}
        if not self._azure_api_version:
            payload["model"] = self._model

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._chat_url(),
                headers=self._request_headers(),
                json=payload,
            )
        if response.status_code != 200:
            logger.error("openai_request_failed", status=response.status_code, body=response.text)
            raise ValidationError(f"AI provider error: {response.status_code} — {response.text[:200]}")

        content = response.json()["choices"][0]["message"]["content"]
        return _parse_json_content(content)

    async def parse_resume(self, resume_text: str) -> dict[str, Any]:
        return await self._chat_json(
            PARSE_RESUME_PROMPT,
            f"Resume text:\n\n{resume_text[:50000]}",
        )

    async def build_resume(
        self,
        candidate_profile: dict[str, Any],
        parsed_resume: dict[str, Any],
        job_description: str,
        recruiter_notes: str | None = None,
        build_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        user_payload = {
            "candidate_profile": candidate_profile,
            "parsed_resume": parsed_resume,
            "job_description": job_description,
            "recruiter_notes": recruiter_notes or "",
            "build_context": build_context or {},
        }
        return await self._chat_json(BUILD_RESUME_PROMPT, json.dumps(user_payload))

    async def score_resume(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> dict[str, Any]:
        user_payload = {
            "resume": resume_json,
            "job_description": job_description,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
        }
        return await self._chat_json(SCORE_RESUME_PROMPT, json.dumps(user_payload))

    async def convert_upload_to_jinja_template(
        self,
        source_html: str | None,
        parsed_resume: dict[str, Any],
    ) -> dict[str, Any]:
        user_payload = {
            "source_html": source_html or "",
            "parsed_resume": parsed_resume,
        }
        return await self._chat_json(CONVERT_UPLOAD_TEMPLATE_PROMPT, json.dumps(user_payload))

    async def generate_interview_question(
        self,
        resume_json: dict[str, Any],
        job_description: str,
        previous_questions: list[str],
        previous_answers: list[str],
        question_type: str = "mcq",
        question_number: int = 1,
    ) -> dict[str, Any]:
        prompts = {
            "mcq": GENERATE_MCQ_PROMPT,
            "scenario": GENERATE_SCENARIO_PROMPT,
            "coding": GENERATE_CODING_PROMPT,
        }
        system = prompts.get(question_type, GENERATE_MCQ_PROMPT)
        user_payload = {
            "resume": resume_json,
            "job_description": job_description,
            "previous_questions": previous_questions,
            "previous_answers": previous_answers,
            "question_type": question_type,
            "question_number": question_number,
        }
        result = await self._chat_json(system, json.dumps(user_payload))
        if question_type != "mcq":
            result.setdefault("options", [])
        return result

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        resume_json: dict[str, Any],
        job_description: str,
    ) -> dict[str, Any]:
        user_payload = {
            "question": question,
            "answer": answer,
            "resume": resume_json,
            "job_description": job_description,
        }
        return await self._chat_json(EVALUATE_ANSWER_PROMPT, json.dumps(user_payload))

    async def summarize_interview(
        self,
        transcript: list[dict[str, str]],
        resume_json: dict[str, Any],
        job_description: str,
        coding_evaluations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        user_payload = {
            "transcript": transcript,
            "resume": resume_json,
            "job_description": job_description,
            "coding_evaluations": coding_evaluations or [],
        }
        return await self._chat_json(SUMMARIZE_INTERVIEW_PROMPT, json.dumps(user_payload))
