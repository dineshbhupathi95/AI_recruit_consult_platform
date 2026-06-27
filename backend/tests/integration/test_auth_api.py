"""Integration tests for authentication API."""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "organization_name": "Test Recruiters",
    "email": "admin@testrecruiters.com",
    "password": "SecurePass123",
    "first_name": "Jane",
    "last_name": "Recruiter",
}


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_register_success(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == REGISTER_PAYLOAD["email"]
        assert data["tenant"]["name"] == REGISTER_PAYLOAD["organization_name"]
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert "admin" in [r["name"] for r in data["user"]["roles"]]

    async def test_register_duplicate_email_fails(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert response.status_code == 409

    async def test_login_success(self, client: AsyncClient) -> None:
        await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": REGISTER_PAYLOAD["email"],
                "password": REGISTER_PAYLOAD["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tokens"]["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.com", "password": "WrongPass123"},
        )
        assert response.status_code == 401

    async def test_get_me_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_success(self, client: AsyncClient) -> None:
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        token = reg.json()["tokens"]["access_token"]
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == REGISTER_PAYLOAD["email"]

    async def test_refresh_token(self, client: AsyncClient) -> None:
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        refresh = reg.json()["tokens"]["refresh_token"]
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_logout(self, client: AsyncClient) -> None:
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        refresh = reg.json()["tokens"]["refresh_token"]
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 200
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert refresh_response.status_code == 401

    async def test_health_check(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
