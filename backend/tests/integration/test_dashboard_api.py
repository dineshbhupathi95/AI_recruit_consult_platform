"""Integration tests for dashboard API."""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "organization_name": "Dashboard Test Agency",
    "email": "admin@dashboardtest.com",
    "password": "SecurePass123",
    "first_name": "Dash",
    "last_name": "Admin",
}


@pytest.mark.asyncio
class TestDashboardAPI:
    async def test_dashboard_overview(self, client: AsyncClient) -> None:
        reg = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        token = reg.json()["tokens"]["access_token"]

        await client.post(
            "/api/v1/clients",
            json={"name": "Dashboard Client", "status": "active"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/api/v1/dashboard/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "pipeline" in data
        assert "recent_activity" in data
        assert len(data["stats"]) >= 4
        assert data["clients_by_status"].get("active", 0) >= 1

    async def test_dashboard_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/dashboard/overview")
        assert response.status_code == 401
