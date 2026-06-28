"""Client management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query, Request, status

from app.core.dependencies import ClientServiceDep, CurrentUser
from app.schemas.auth import MessageResponse
from app.schemas.client import (
    ClientContactCreate,
    ClientContactResponse,
    ClientContactUpdate,
    ClientCreate,
    ClientDetailResponse,
    ClientListResponse,
    ClientLocationCreate,
    ClientLocationResponse,
    ClientLocationUpdate,
    ClientNoteCreate,
    ClientNoteResponse,
    ClientStatus,
    ClientUpdate,
)

router = APIRouter(prefix="/clients", tags=["Client Management"])


def _client_info(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.get(
    "",
    response_model=ClientListResponse,
    summary="List clients",
    description="List client companies with search, status filter, and pagination.",
)
async def list_clients(
    current_user: CurrentUser,
    client_service: ClientServiceDep,
    search: str | None = Query(default=None, max_length=255),
    status: ClientStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ClientListResponse:
    current_user.require_permission("clients:read")
    return await client_service.list_clients(
        current_user.tenant_id,
        search=search,
        status=status,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ClientDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create client",
    description="Create a new client company with optional contacts and locations.",
)
async def create_client(
    data: ClientCreate,
    request: Request,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientDetailResponse:
    current_user.require_permission("clients:write")
    user_agent, ip_address = _client_info(request)
    return await client_service.create_client(
        current_user.tenant_id,
        data,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get(
    "/{client_id}",
    response_model=ClientDetailResponse,
    summary="Get client",
    description="Get full client detail including contacts, locations, and notes.",
)
async def get_client(
    client_id: UUID,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientDetailResponse:
    current_user.require_permission("clients:read")
    return await client_service.get_client(client_id, current_user.tenant_id)


@router.patch(
    "/{client_id}",
    response_model=ClientDetailResponse,
    summary="Update client",
    description="Update client company details.",
)
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    request: Request,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientDetailResponse:
    current_user.require_permission("clients:write")
    user_agent, ip_address = _client_info(request)
    return await client_service.update_client(
        client_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.delete(
    "/{client_id}",
    response_model=MessageResponse,
    summary="Delete client",
    description="Soft delete a client company.",
)
async def delete_client(
    client_id: UUID,
    request: Request,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> MessageResponse:
    current_user.require_permission("clients:write")
    user_agent, ip_address = _client_info(request)
    await client_service.delete_client(
        client_id,
        current_user.tenant_id,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return MessageResponse(message="Client deleted successfully")


@router.post(
    "/{client_id}/contacts",
    response_model=ClientContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add contact",
)
async def add_contact(
    client_id: UUID,
    data: ClientContactCreate,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientContactResponse:
    current_user.require_permission("clients:write")
    return await client_service.add_contact(
        client_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
    )


@router.patch(
    "/{client_id}/contacts/{contact_id}",
    response_model=ClientContactResponse,
    summary="Update contact",
)
async def update_contact(
    client_id: UUID,
    contact_id: UUID,
    data: ClientContactUpdate,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientContactResponse:
    current_user.require_permission("clients:write")
    return await client_service.update_contact(
        client_id,
        contact_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
    )


@router.delete(
    "/{client_id}/contacts/{contact_id}",
    response_model=MessageResponse,
    summary="Delete contact",
)
async def delete_contact(
    client_id: UUID,
    contact_id: UUID,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> MessageResponse:
    current_user.require_permission("clients:write")
    await client_service.delete_contact(
        client_id,
        contact_id,
        current_user.tenant_id,
        current_user.user_id,
    )
    return MessageResponse(message="Contact deleted successfully")


@router.post(
    "/{client_id}/locations",
    response_model=ClientLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add location",
)
async def add_location(
    client_id: UUID,
    data: ClientLocationCreate,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientLocationResponse:
    current_user.require_permission("clients:write")
    return await client_service.add_location(
        client_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
    )


@router.patch(
    "/{client_id}/locations/{location_id}",
    response_model=ClientLocationResponse,
    summary="Update location",
)
async def update_location(
    client_id: UUID,
    location_id: UUID,
    data: ClientLocationUpdate,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientLocationResponse:
    current_user.require_permission("clients:write")
    return await client_service.update_location(
        client_id,
        location_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
    )


@router.delete(
    "/{client_id}/locations/{location_id}",
    response_model=MessageResponse,
    summary="Delete location",
)
async def delete_location(
    client_id: UUID,
    location_id: UUID,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> MessageResponse:
    current_user.require_permission("clients:write")
    await client_service.delete_location(
        client_id,
        location_id,
        current_user.tenant_id,
        current_user.user_id,
    )
    return MessageResponse(message="Location deleted successfully")


@router.post(
    "/{client_id}/notes",
    response_model=ClientNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add note",
)
async def add_note(
    client_id: UUID,
    data: ClientNoteCreate,
    current_user: CurrentUser,
    client_service: ClientServiceDep,
) -> ClientNoteResponse:
    current_user.require_permission("clients:write")
    return await client_service.add_note(
        client_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
    )
