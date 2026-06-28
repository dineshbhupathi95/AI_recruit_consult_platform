"""Integration tests for resume template API."""

from io import BytesIO

import pytest
from docx import Document
from httpx import AsyncClient

from tests.integration.test_candidates_api import REGISTER_PAYLOAD, _make_resume_docx, _setup_full_context


@pytest.mark.asyncio
class TestResumeTemplateAPI:
    async def test_list_and_preview_system_templates(self, client: AsyncClient) -> None:
        token, _, _ = await _setup_full_context(client)
        headers = {"Authorization": f"Bearer {token}"}

        listing = await client.get("/api/v1/resume-templates", headers=headers)
        assert listing.status_code == 200
        body = listing.json()
        assert body["total"] >= 3
        assert any(t["name"] == "Classic Professional" for t in body["items"])

        template_id = body["items"][0]["id"]
        preview = await client.get(f"/api/v1/resume-templates/{template_id}/preview", headers=headers)
        assert preview.status_code == 200
        assert "Jane Doe" in preview.text or "Candidate" in preview.text

    async def test_upload_resume_as_template(self, client: AsyncClient) -> None:
        token, _, _ = await _setup_full_context(client)
        headers = {"Authorization": f"Bearer {token}"}
        resume_bytes = _make_resume_docx()

        upload = await client.post(
            "/api/v1/resume-templates/upload",
            headers=headers,
            files={
                "file": (
                    "my_layout.docx",
                    resume_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"name": "My Uploaded Layout", "is_default": "false"},
        )
        assert upload.status_code == 201
        body = upload.json()
        assert body["name"] == "My Uploaded Layout"
        assert body["config"]["source_type"] == "upload"
        assert body["config"]["source_file_name"] == "my_layout.docx"

        source = await client.get(f"/api/v1/resume-templates/{body['id']}/source", headers=headers)
        assert source.status_code == 200
        assert len(source.content) > 0

    async def test_create_custom_template(self, client: AsyncClient) -> None:
        reg = await client.post("/api/v1/auth/register", json={
            **REGISTER_PAYLOAD,
            "organization_name": "Template Co",
            "email": "tpl@templateco.com",
        })
        headers = {"Authorization": f"Bearer {reg.json()["tokens"]["access_token"]}"}

        created = await client.post(
            "/api/v1/resume-templates",
            headers=headers,
            json={
                "name": "Custom Blue",
                "description": "Test layout",
                "html_template": "<h1>{{ resume.basic_details.full_name }}</h1>",
                "css_styles": "h1 { color: blue; }",
            },
        )
        assert created.status_code == 201
        assert created.json()["name"] == "Custom Blue"
        assert created.json()["is_system"] is False
