"""Client management business logic."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.client import Client, ClientContact, ClientLocation, ContactType
from app.repositories.client_repository import (
    ClientContactRepository,
    ClientLocationRepository,
    ClientNoteRepository,
    ClientRepository,
)
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
    ClientSummaryResponse,
    ClientUpdate,
    ContactType as ContactTypeSchema,
)
from app.services.audit_service import AuditService

logger = get_logger(__name__)


class ClientService:
    """Service layer for client management operations."""

    def __init__(
        self,
        client_repo: ClientRepository,
        contact_repo: ClientContactRepository,
        location_repo: ClientLocationRepository,
        note_repo: ClientNoteRepository,
        audit_service: AuditService,
    ) -> None:
        self._client_repo = client_repo
        self._contact_repo = contact_repo
        self._location_repo = location_repo
        self._note_repo = note_repo
        self._audit_service = audit_service

    @staticmethod
    def _build_contact_response(contact: ClientContact) -> ClientContactResponse:
        return ClientContactResponse(
            id=contact.id,
            client_id=contact.client_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            full_name=contact.full_name,
            email=contact.email,
            phone=contact.phone,
            job_title=contact.job_title,
            department=contact.department,
            contact_type=ContactTypeSchema(
                contact.contact_type.value
                if hasattr(contact.contact_type, "value")
                else contact.contact_type
            ),
            is_active=contact.is_active,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )

    @staticmethod
    def _build_location_response(location: ClientLocation) -> ClientLocationResponse:
        return ClientLocationResponse.model_validate(location)

    @staticmethod
    def _build_summary(client: Client) -> ClientSummaryResponse:
        active_contacts = [c for c in client.contacts if not c.is_deleted]
        active_locations = [loc for loc in client.locations if not loc.is_deleted]
        hiring_managers = [
            c for c in active_contacts
            if c.contact_type == ContactType.HIRING_MANAGER and c.is_active
        ]
        return ClientSummaryResponse(
            id=client.id,
            name=client.name,
            industry=client.industry,
            status=ClientService._status_value(client.status),
            email=client.email,
            phone=client.phone,
            contact_count=len(active_contacts),
            location_count=len(active_locations),
            hiring_manager_count=len(hiring_managers),
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    @staticmethod
    def _status_value(status: ClientStatus | str) -> ClientStatus:
        if isinstance(status, ClientStatus):
            return status
        return ClientStatus(status)

    def _build_detail(self, client: Client) -> ClientDetailResponse:
        active_contacts = [c for c in client.contacts if not c.is_deleted]
        active_locations = [loc for loc in client.locations if not loc.is_deleted]
        return ClientDetailResponse(
            id=client.id,
            tenant_id=client.tenant_id,
            name=client.name,
            legal_name=client.legal_name,
            industry=client.industry,
            website=client.website,
            phone=client.phone,
            email=client.email,
            status=ClientService._status_value(client.status),
            description=client.description,
            contacts=[self._build_contact_response(c) for c in active_contacts],
            locations=[self._build_location_response(loc) for loc in active_locations],
            notes=[ClientNoteResponse.model_validate(n) for n in client.notes],
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    async def _get_client_or_raise(
        self,
        client_id: UUID,
        tenant_id: UUID,
        *,
        include_relations: bool = False,
    ) -> Client:
        client = await self._client_repo.get_by_id_for_tenant(
            client_id,
            tenant_id,
            include_relations=include_relations,
        )
        if client is None:
            raise NotFoundError("Client not found")
        return client

    async def list_clients(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        status: ClientStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ClientListResponse:
        """List clients with search and pagination."""
        clients, total = await self._client_repo.list_for_tenant(
            tenant_id,
            search=search,
            status=status.value if status else None,
            page=page,
            page_size=page_size,
        )
        return ClientListResponse(
            items=[self._build_summary(c) for c in clients],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=self._client_repo.total_pages(total, page_size),
        )

    async def get_client(self, client_id: UUID, tenant_id: UUID) -> ClientDetailResponse:
        """Get full client detail."""
        client = await self._get_client_or_raise(
            client_id,
            tenant_id,
            include_relations=True,
        )
        return self._build_detail(client)

    async def create_client(
        self,
        tenant_id: UUID,
        data: ClientCreate,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ClientDetailResponse:
        """Create a new client with optional contacts and locations."""
        try:
            client = await self._client_repo.create(
                tenant_id,
                name=data.name,
                legal_name=data.legal_name,
                industry=data.industry,
                website=data.website,
                phone=data.phone,
                email=str(data.email) if data.email else None,
                status=data.status.value,
                description=data.description,
                created_by=user_id,
            )

            for contact_data in data.contacts:
                await self._contact_repo.create(
                    tenant_id,
                    client.id,
                    first_name=contact_data.first_name,
                    last_name=contact_data.last_name,
                    email=str(contact_data.email),
                    phone=contact_data.phone,
                    job_title=contact_data.job_title,
                    department=contact_data.department,
                    contact_type=contact_data.contact_type.value,
                    is_active=contact_data.is_active,
                    created_by=user_id,
                )

            for location_data in data.locations:
                await self._location_repo.create(
                    tenant_id,
                    client.id,
                    name=location_data.name,
                    address_line1=location_data.address_line1,
                    address_line2=location_data.address_line2,
                    city=location_data.city,
                    state=location_data.state,
                    country=location_data.country,
                    postal_code=location_data.postal_code,
                    is_headquarters=location_data.is_headquarters,
                    created_by=user_id,
                )
        except IntegrityError as exc:
            raise ConflictError("A client with this information already exists") from exc

        await self._audit_service.log(
            tenant_id,
            "client.created",
            "client",
            user_id=user_id,
            resource_id=str(client.id),
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Created client: {data.name}",
        )

        logger.info("client_created", client_id=str(client.id), tenant_id=str(tenant_id))
        return await self.get_client(client.id, tenant_id)

    async def update_client(
        self,
        client_id: UUID,
        tenant_id: UUID,
        data: ClientUpdate,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ClientDetailResponse:
        """Update client company details."""
        client = await self._get_client_or_raise(client_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise ValidationError("No fields provided for update")

        changes: dict[str, dict[str, str | None]] = {}
        for field, value in update_data.items():
            old_value = getattr(client, field)
            if field == "status" and value is not None:
                value = value.value if hasattr(value, "value") else value
            if field == "email" and value is not None:
                value = str(value)
            if old_value != value:
                changes[field] = {
                    "old": str(old_value) if old_value is not None else None,
                    "new": str(value) if value is not None else None,
                }
                setattr(client, field, value)

        client.updated_by = user_id
        await self._client_repo._session.flush()

        await self._audit_service.log(
            tenant_id,
            "client.updated",
            "client",
            user_id=user_id,
            resource_id=str(client_id),
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            description=f"Updated client: {client.name}",
        )

        logger.info("client_updated", client_id=str(client_id), tenant_id=str(tenant_id))
        return await self.get_client(client_id, tenant_id)

    async def delete_client(
        self,
        client_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Soft delete a client."""
        client = await self._get_client_or_raise(client_id, tenant_id)
        await self._client_repo.soft_delete(client, deleted_by=user_id)

        await self._audit_service.log(
            tenant_id,
            "client.deleted",
            "client",
            user_id=user_id,
            resource_id=str(client_id),
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Deleted client: {client.name}",
        )

        logger.info("client_deleted", client_id=str(client_id), tenant_id=str(tenant_id))

    async def add_contact(
        self,
        client_id: UUID,
        tenant_id: UUID,
        data: ClientContactCreate,
        user_id: UUID,
    ) -> ClientContactResponse:
        """Add a contact to a client."""
        await self._get_client_or_raise(client_id, tenant_id)
        try:
            contact = await self._contact_repo.create(
                tenant_id,
                client_id,
                first_name=data.first_name,
                last_name=data.last_name,
                email=str(data.email),
                phone=data.phone,
                job_title=data.job_title,
                department=data.department,
                contact_type=data.contact_type.value,
                is_active=data.is_active,
                created_by=user_id,
            )
        except IntegrityError as exc:
            raise ConflictError("A contact with this email already exists for this client") from exc

        await self._audit_service.log(
            tenant_id,
            "client.contact.created",
            "client_contact",
            user_id=user_id,
            resource_id=str(contact.id),
            description=f"Added contact {contact.full_name} to client",
        )
        return self._build_contact_response(contact)

    async def update_contact(
        self,
        client_id: UUID,
        contact_id: UUID,
        tenant_id: UUID,
        data: ClientContactUpdate,
        user_id: UUID,
    ) -> ClientContactResponse:
        """Update a client contact."""
        contact = await self._contact_repo.get_by_id_for_client(contact_id, client_id, tenant_id)
        if contact is None:
            raise NotFoundError("Contact not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("No fields provided for update")

        for field, value in update_data.items():
            if field == "contact_type" and value is not None:
                value = value.value
            if field == "email" and value is not None:
                value = str(value)
            setattr(contact, field, value)

        contact.updated_by = user_id
        await self._contact_repo._session.flush()
        await self._contact_repo._session.refresh(contact)
        return self._build_contact_response(contact)

    async def delete_contact(
        self,
        client_id: UUID,
        contact_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> None:
        """Soft delete a client contact."""
        contact = await self._contact_repo.get_by_id_for_client(contact_id, client_id, tenant_id)
        if contact is None:
            raise NotFoundError("Contact not found")
        await self._contact_repo.soft_delete(contact, deleted_by=user_id)

    async def add_location(
        self,
        client_id: UUID,
        tenant_id: UUID,
        data: ClientLocationCreate,
        user_id: UUID,
    ) -> ClientLocationResponse:
        """Add a location to a client."""
        await self._get_client_or_raise(client_id, tenant_id)
        location = await self._location_repo.create(
            tenant_id,
            client_id,
            name=data.name,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            country=data.country,
            postal_code=data.postal_code,
            is_headquarters=data.is_headquarters,
            created_by=user_id,
        )

        await self._audit_service.log(
            tenant_id,
            "client.location.created",
            "client_location",
            user_id=user_id,
            resource_id=str(location.id),
            description=f"Added location {location.name} to client",
        )
        return self._build_location_response(location)

    async def update_location(
        self,
        client_id: UUID,
        location_id: UUID,
        tenant_id: UUID,
        data: ClientLocationUpdate,
        user_id: UUID,
    ) -> ClientLocationResponse:
        """Update a client location."""
        location = await self._location_repo.get_by_id_for_client(
            location_id, client_id, tenant_id
        )
        if location is None:
            raise NotFoundError("Location not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("No fields provided for update")

        for field, value in update_data.items():
            setattr(location, field, value)

        location.updated_by = user_id
        await self._location_repo._session.flush()
        await self._location_repo._session.refresh(location)
        return self._build_location_response(location)

    async def delete_location(
        self,
        client_id: UUID,
        location_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> None:
        """Soft delete a client location."""
        location = await self._location_repo.get_by_id_for_client(
            location_id, client_id, tenant_id
        )
        if location is None:
            raise NotFoundError("Location not found")
        await self._location_repo.soft_delete(location, deleted_by=user_id)

    async def add_note(
        self,
        client_id: UUID,
        tenant_id: UUID,
        data: ClientNoteCreate,
        user_id: UUID,
    ) -> ClientNoteResponse:
        """Add a note to a client."""
        await self._get_client_or_raise(client_id, tenant_id)
        note = await self._note_repo.create(
            tenant_id,
            client_id,
            data.content,
            created_by=user_id,
        )

        await self._audit_service.log(
            tenant_id,
            "client.note.created",
            "client_note",
            user_id=user_id,
            resource_id=str(note.id),
            description="Added note to client",
        )
        return ClientNoteResponse.model_validate(note)
