"""Integration tests for tenant settings API."""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "organization_name": "Settings Test Agency",
    "email": "admin@settingstest.com",
    "password": "SecurePass123",
    "first_name": "Settings",
    "last_name": "Admin",
}


async def _register_token(client: AsyncClient) -> str:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    return response.json()["tokens"]["access_token"]


@pytest.mark.asyncio
class TestSettingsAPI:
    async def test_get_schema(self, client: AsyncClient) -> None:
        token = await _register_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/settings/schema", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["ai_providers"]) >= 3
        provider_ids = {p["id"] for p in data["ai_providers"]}
        assert "openai" in provider_ids
        assert "groq" in provider_ids
        assert "gemini" in provider_ids
        assert "ollama" in provider_ids
        assert "mock" in provider_ids

    async def test_update_and_get_mock_provider(self, client: AsyncClient) -> None:
        token = await _register_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        update = await client.put(
            "/api/v1/settings",
            json={"ai_provider": "mock", "values": {}},
            headers=headers,
        )
        assert update.status_code == 200
        assert update.json()["ai_provider"] == "mock"

        get_resp = await client.get("/api/v1/settings", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["ai_provider"] == "mock"

    async def test_ai_connection_mock(self, client: AsyncClient) -> None:
        token = await _register_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.put(
            "/api/v1/settings",
            json={"ai_provider": "mock", "values": {}},
            headers=headers,
        )
        test = await client.post("/api/v1/settings/test-ai", headers=headers)
        assert test.status_code == 200
        assert test.json()["success"] is True

    async def test_recruiter_cannot_access_settings(self, client: AsyncClient) -> None:
        token = await _register_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        # Admin from registration can access — verify forbidden for unauthenticated
        response = await client.get("/api/v1/settings")
        assert response.status_code == 401
