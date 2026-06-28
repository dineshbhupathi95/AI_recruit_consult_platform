"""Integration tests for client management API."""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "organization_name": "Client Test Agency",
    "email": "admin@clienttest.com",
    "password": "SecurePass123",
    "first_name": "Admin",
    "last_name": "User",
}

CLIENT_PAYLOAD = {
    "name": "Acme Corporation",
    "industry": "Technology",
    "website": "https://acme.example.com",
    "phone": "+1-555-0100",
    "email": "info@acme.example.com",
    "status": "active",
    "description": "Enterprise software client",
    "contacts": [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@acme.example.com",
            "phone": "+1-555-0101",
            "job_title": "VP Engineering",
            "contact_type": "hiring_manager",
        }
    ],
    "locations": [
        {
            "name": "San Francisco HQ",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "is_headquarters": True,
        }
    ],
}


async def _register_and_get_token(client: AsyncClient) -> str:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    return response.json()["tokens"]["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestClientAPI:
    async def test_create_client_success(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        response = await client.post(
            "/api/v1/clients",
            json=CLIENT_PAYLOAD,
            headers=_auth_headers(token),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == CLIENT_PAYLOAD["name"]
        assert len(data["contacts"]) == 1
        assert data["contacts"][0]["contact_type"] == "hiring_manager"
        assert len(data["locations"]) == 1

    async def test_list_clients(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        await client.post(
            "/api/v1/clients",
            json=CLIENT_PAYLOAD,
            headers=_auth_headers(token),
        )
        response = await client.get(
            "/api/v1/clients",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["hiring_manager_count"] == 1

    async def test_get_client_detail(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        create = await client.post(
            "/api/v1/clients",
            json=CLIENT_PAYLOAD,
            headers=_auth_headers(token),
        )
        client_id = create.json()["id"]
        response = await client.get(
            f"/api/v1/clients/{client_id}",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Acme Corporation"

    async def test_update_client(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        create = await client.post(
            "/api/v1/clients",
            json=CLIENT_PAYLOAD,
            headers=_auth_headers(token),
        )
        client_id = create.json()["id"]
        response = await client.patch(
            f"/api/v1/clients/{client_id}",
            json={"name": "Acme Corp Updated", "status": "on_hold"},
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Acme Corp Updated"
        assert response.json()["status"] == "on_hold"

    async def test_add_contact(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        create = await client.post(
            "/api/v1/clients",
            json={"name": "Beta Inc", "status": "prospect"},
            headers=_auth_headers(token),
        )
        client_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/clients/{client_id}/contacts",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@beta.com",
                "contact_type": "primary",
            },
            headers=_auth_headers(token),
        )
        assert response.status_code == 201
        assert response.json()["full_name"] == "Jane Doe"

    async def test_add_note(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        create = await client.post(
            "/api/v1/clients",
            json={"name": "Gamma LLC", "status": "prospect"},
            headers=_auth_headers(token),
        )
        client_id = create.json()["id"]
        response = await client.post(
            f"/api/v1/clients/{client_id}/notes",
            json={"content": "Initial discovery call completed."},
            headers=_auth_headers(token),
        )
        assert response.status_code == 201
        assert "discovery" in response.json()["content"]

    async def test_delete_client(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        create = await client.post(
            "/api/v1/clients",
            json={"name": "To Delete Corp", "status": "inactive"},
            headers=_auth_headers(token),
        )
        client_id = create.json()["id"]
        response = await client.delete(
            f"/api/v1/clients/{client_id}",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        get_response = await client.get(
            f"/api/v1/clients/{client_id}",
            headers=_auth_headers(token),
        )
        assert get_response.status_code == 404

    async def test_clients_require_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/clients")
        assert response.status_code == 401

    async def test_search_clients(self, client: AsyncClient) -> None:
        token = await _register_and_get_token(client)
        await client.post(
            "/api/v1/clients",
            json={"name": "Searchable Corp", "industry": "Finance"},
            headers=_auth_headers(token),
        )
        await client.post(
            "/api/v1/clients",
            json={"name": "Other Corp", "industry": "Retail"},
            headers=_auth_headers(token),
        )
        response = await client.get(
            "/api/v1/clients?search=Searchable",
            headers=_auth_headers(token),
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1
