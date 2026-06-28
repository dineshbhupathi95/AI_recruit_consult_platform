"""Integration tests for job requirements API."""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "organization_name": "Job Test Agency",
    "email": "admin@jobtest.com",
    "password": "SecurePass123",
    "first_name": "Job",
    "last_name": "Admin",
}

CLIENT_PAYLOAD = {
    "name": "TechCorp Inc",
    "status": "active",
    "contacts": [
        {
            "first_name": "Sarah",
            "last_name": "Hiring",
            "email": "sarah@techcorp.com",
            "contact_type": "hiring_manager",
        }
    ],
}

JOB_PAYLOAD = {
    "title": "Senior Python Developer",
    "employment_type": "full_time",
    "priority": "high",
    "status": "open",
    "experience_min_years": 5,
    "experience_max_years": 10,
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["AWS", "Docker"],
    "description": "Build scalable backend services.",
}


async def _setup_client_and_token(client: AsyncClient) -> tuple[str, str, str]:
    reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    token = reg.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client_resp = await client.post("/api/v1/clients", json=CLIENT_PAYLOAD, headers=headers)
    client_id = client_resp.json()["id"]
    hiring_manager_id = client_resp.json()["contacts"][0]["id"]
    return token, client_id, hiring_manager_id


@pytest.mark.asyncio
class TestJobsAPI:
    async def test_create_job_success(self, client: AsyncClient) -> None:
        token, client_id, hm_id = await _setup_client_and_token(client)
        payload = {**JOB_PAYLOAD, "client_id": client_id, "hiring_manager_id": hm_id}
        response = await client.post(
            "/api/v1/jobs",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == JOB_PAYLOAD["title"]
        assert data["client_name"] == "TechCorp Inc"
        assert len(data["required_skills"]) == 3

    async def test_list_jobs(self, client: AsyncClient) -> None:
        token, client_id, _ = await _setup_client_and_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post("/api/v1/jobs", json={**JOB_PAYLOAD, "client_id": client_id}, headers=headers)
        response = await client.get("/api/v1/jobs", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    async def test_get_job_detail(self, client: AsyncClient) -> None:
        token, client_id, _ = await _setup_client_and_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = await client.post(
            "/api/v1/jobs",
            json={**JOB_PAYLOAD, "client_id": client_id},
            headers=headers,
        )
        job_id = create.json()["id"]
        response = await client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "open"

    async def test_update_job(self, client: AsyncClient) -> None:
        token, client_id, _ = await _setup_client_and_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = await client.post(
            "/api/v1/jobs",
            json={**JOB_PAYLOAD, "client_id": client_id},
            headers=headers,
        )
        job_id = create.json()["id"]
        response = await client.patch(
            f"/api/v1/jobs/{job_id}",
            json={"title": "Lead Python Developer", "priority": "urgent"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Lead Python Developer"
        assert response.json()["priority"] == "urgent"

    async def test_delete_job(self, client: AsyncClient) -> None:
        token, client_id, _ = await _setup_client_and_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create = await client.post(
            "/api/v1/jobs",
            json={**JOB_PAYLOAD, "client_id": client_id},
            headers=headers,
        )
        job_id = create.json()["id"]
        response = await client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
        assert response.status_code == 200
        get_resp = await client.get(f"/api/v1/jobs/{job_id}", headers=headers)
        assert get_resp.status_code == 404

    async def test_jobs_require_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 401

    async def test_filter_by_client(self, client: AsyncClient) -> None:
        token, client_id, _ = await _setup_client_and_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post("/api/v1/jobs", json={**JOB_PAYLOAD, "client_id": client_id}, headers=headers)
        response = await client.get(f"/api/v1/jobs?client_id={client_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1
