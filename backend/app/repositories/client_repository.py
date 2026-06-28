"""Client data access layer."""

from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.client import Client, ClientContact, ClientLocation, ClientNote, ContactType
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Repository for client company CRUD and search."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)

    async def get_by_id_for_tenant(
        self,
        client_id: UUID,
        tenant_id: UUID,
        *,
        include_relations: bool = False,
    ) -> Client | None:
        """Fetch client scoped to tenant."""
        query = select(Client).where(
            Client.id == client_id,
            Client.tenant_id == tenant_id,
            Client.is_deleted.is_(False),
        )
        if include_relations:
            query = query.options(
                selectinload(Client.contacts),
                selectinload(Client.locations),
                selectinload(Client.notes),
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Client], int]:
        """List clients with optional search and pagination."""
        base_query = select(Client).where(
            Client.tenant_id == tenant_id,
            Client.is_deleted.is_(False),
        )

        if status:
            base_query = base_query.where(Client.status == status)

        if search:
            pattern = f"%{search}%"
            base_query = base_query.where(
                or_(
                    Client.name.ilike(pattern),
                    Client.industry.ilike(pattern),
                    Client.email.ilike(pattern),
                )
            )

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = (
            base_query.options(
                selectinload(Client.contacts),
                selectinload(Client.locations),
            )
            .order_by(Client.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(
        self,
        tenant_id: UUID,
        *,
        name: str,
        legal_name: str | None = None,
        industry: str | None = None,
        website: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        status: str = "prospect",
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> Client:
        """Create a new client."""
        client = Client(
            tenant_id=tenant_id,
            name=name,
            legal_name=legal_name,
            industry=industry,
            website=website,
            phone=phone,
            email=email,
            status=status,
            description=description,
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.add(client)

    async def soft_delete(self, client: Client, deleted_by: UUID | None = None) -> Client:
        """Soft delete a client."""
        client.is_deleted = True
        client.deleted_at = datetime.now(timezone.utc)
        client.updated_by = deleted_by
        await self._session.flush()
        await self._session.refresh(client)
        return client

    async def count_by_status(self, tenant_id: UUID) -> dict[str, int]:
        """Count clients grouped by status."""
        query = (
            select(Client.status, func.count(Client.id))
            .where(Client.tenant_id == tenant_id, Client.is_deleted.is_(False))
            .group_by(Client.status)
        )
        result = await self._session.execute(query)
        return {str(row[0].value): row[1] for row in result.all()}

    async def count_total(self, tenant_id: UUID) -> int:
        """Count total active clients."""
        query = select(func.count(Client.id)).where(
            Client.tenant_id == tenant_id,
            Client.is_deleted.is_(False),
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    @staticmethod
    def total_pages(total: int, page_size: int) -> int:
        """Calculate total pages for pagination."""
        if total == 0:
            return 0
        return ceil(total / page_size)


class ClientContactRepository(BaseRepository[ClientContact]):
    """Repository for client contacts."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientContact)

    async def get_by_id_for_client(
        self,
        contact_id: UUID,
        client_id: UUID,
        tenant_id: UUID,
    ) -> ClientContact | None:
        """Fetch contact scoped to client and tenant."""
        result = await self._session.execute(
            select(ClientContact).where(
                ClientContact.id == contact_id,
                ClientContact.client_id == client_id,
                ClientContact.tenant_id == tenant_id,
                ClientContact.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: UUID,
        client_id: UUID,
        *,
        first_name: str,
        last_name: str,
        email: str,
        phone: str | None = None,
        job_title: str | None = None,
        department: str | None = None,
        contact_type: str = "general",
        is_active: bool = True,
        created_by: UUID | None = None,
    ) -> ClientContact:
        """Create a client contact."""
        contact = ClientContact(
            tenant_id=tenant_id,
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            job_title=job_title,
            department=department,
            contact_type=contact_type,
            is_active=is_active,
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.add(contact)

    async def soft_delete(
        self,
        contact: ClientContact,
        deleted_by: UUID | None = None,
    ) -> ClientContact:
        """Soft delete a contact."""
        contact.is_deleted = True
        contact.deleted_at = datetime.now(timezone.utc)
        contact.updated_by = deleted_by
        await self._session.flush()
        await self._session.refresh(contact)
        return contact

    async def count_hiring_managers(self, tenant_id: UUID) -> int:
        """Count active hiring manager contacts."""
        query = select(func.count(ClientContact.id)).where(
            ClientContact.tenant_id == tenant_id,
            ClientContact.contact_type == ContactType.HIRING_MANAGER,
            ClientContact.is_deleted.is_(False),
            ClientContact.is_active.is_(True),
        )
        result = await self._session.execute(query)
        return result.scalar_one()


class ClientLocationRepository(BaseRepository[ClientLocation]):
    """Repository for client locations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientLocation)

    async def get_by_id_for_client(
        self,
        location_id: UUID,
        client_id: UUID,
        tenant_id: UUID,
    ) -> ClientLocation | None:
        """Fetch location scoped to client and tenant."""
        result = await self._session.execute(
            select(ClientLocation).where(
                ClientLocation.id == location_id,
                ClientLocation.client_id == client_id,
                ClientLocation.tenant_id == tenant_id,
                ClientLocation.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: UUID,
        client_id: UUID,
        *,
        name: str,
        address_line1: str | None = None,
        address_line2: str | None = None,
        city: str | None = None,
        state: str | None = None,
        country: str | None = None,
        postal_code: str | None = None,
        is_headquarters: bool = False,
        created_by: UUID | None = None,
    ) -> ClientLocation:
        """Create a client location."""
        location = ClientLocation(
            tenant_id=tenant_id,
            client_id=client_id,
            name=name,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            is_headquarters=is_headquarters,
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.add(location)

    async def soft_delete(
        self,
        location: ClientLocation,
        deleted_by: UUID | None = None,
    ) -> ClientLocation:
        """Soft delete a location."""
        location.is_deleted = True
        location.deleted_at = datetime.now(timezone.utc)
        location.updated_by = deleted_by
        await self._session.flush()
        await self._session.refresh(location)
        return location


class ClientNoteRepository(BaseRepository[ClientNote]):
    """Repository for client notes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientNote)

    async def create(
        self,
        tenant_id: UUID,
        client_id: UUID,
        content: str,
        created_by: UUID | None = None,
    ) -> ClientNote:
        """Create a client note."""
        note = ClientNote(
            tenant_id=tenant_id,
            client_id=client_id,
            content=content,
            created_by=created_by,
        )
        return await self.add(note)
