"""Job requirement data access layer."""

from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job_requirement import JobRequirement, JobRequirementAttachment, JobStatus
from app.repositories.base import BaseRepository


class JobRequirementRepository(BaseRepository[JobRequirement]):
    """Repository for job requirement CRUD and search."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, JobRequirement)

    async def get_by_id_for_tenant(
        self,
        job_id: UUID,
        tenant_id: UUID,
        *,
        include_relations: bool = False,
    ) -> JobRequirement | None:
        query = select(JobRequirement).where(
            JobRequirement.id == job_id,
            JobRequirement.tenant_id == tenant_id,
            JobRequirement.is_deleted.is_(False),
        )
        if include_relations:
            query = query.options(
                selectinload(JobRequirement.client),
                selectinload(JobRequirement.hiring_manager),
                selectinload(JobRequirement.client_location),
                selectinload(JobRequirement.attachments),
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        status: str | None = None,
        client_id: UUID | None = None,
        priority: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[JobRequirement], int]:
        from app.models.client import Client

        base_query = (
            select(JobRequirement)
            .join(Client, JobRequirement.client_id == Client.id)
            .where(
                JobRequirement.tenant_id == tenant_id,
                JobRequirement.is_deleted.is_(False),
                Client.is_deleted.is_(False),
            )
        )

        if status:
            base_query = base_query.where(JobRequirement.status == status)
        if client_id:
            base_query = base_query.where(JobRequirement.client_id == client_id)
        if priority:
            base_query = base_query.where(JobRequirement.priority == priority)
        if search:
            pattern = f"%{search}%"
            base_query = base_query.where(
                or_(
                    JobRequirement.title.ilike(pattern),
                    JobRequirement.location_text.ilike(pattern),
                    Client.name.ilike(pattern),
                )
            )

        count_query = select(func.count()).select_from(base_query.subquery())
        total = (await self._session.execute(count_query)).scalar_one()

        query = (
            base_query.options(
                selectinload(JobRequirement.client),
                selectinload(JobRequirement.hiring_manager),
            )
            .order_by(JobRequirement.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(
        self,
        tenant_id: UUID,
        *,
        client_id: UUID,
        title: str,
        hiring_manager_id: UUID | None = None,
        client_location_id: UUID | None = None,
        experience_min_years: int | None = None,
        experience_max_years: int | None = None,
        budget_min=None,
        budget_max=None,
        budget_currency: str = "USD",
        notice_period_days: int | None = None,
        location_text: str | None = None,
        employment_type: str = "full_time",
        priority: str = "medium",
        status: str = "draft",
        description: str | None = None,
        required_skills: list[str] | None = None,
        preferred_skills: list[str] | None = None,
        created_by: UUID | None = None,
    ) -> JobRequirement:
        job = JobRequirement(
            tenant_id=tenant_id,
            client_id=client_id,
            title=title,
            hiring_manager_id=hiring_manager_id,
            client_location_id=client_location_id,
            experience_min_years=experience_min_years,
            experience_max_years=experience_max_years,
            budget_min=budget_min,
            budget_max=budget_max,
            budget_currency=budget_currency,
            notice_period_days=notice_period_days,
            location_text=location_text,
            employment_type=employment_type,
            priority=priority,
            status=status,
            description=description,
            required_skills=required_skills or [],
            preferred_skills=preferred_skills or [],
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.add(job)

    async def soft_delete(self, job: JobRequirement, deleted_by: UUID | None = None) -> JobRequirement:
        job.is_deleted = True
        job.deleted_at = datetime.now(timezone.utc)
        job.updated_by = deleted_by
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def count_active(self, tenant_id: UUID) -> int:
        query = select(func.count(JobRequirement.id)).where(
            JobRequirement.tenant_id == tenant_id,
            JobRequirement.is_deleted.is_(False),
            JobRequirement.status == JobStatus.OPEN,
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    async def count_by_client(self, tenant_id: UUID, client_id: UUID) -> int:
        query = select(func.count(JobRequirement.id)).where(
            JobRequirement.tenant_id == tenant_id,
            JobRequirement.client_id == client_id,
            JobRequirement.is_deleted.is_(False),
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    @staticmethod
    def total_pages(total: int, page_size: int) -> int:
        if total == 0:
            return 0
        return ceil(total / page_size)


class JobRequirementAttachmentRepository(BaseRepository[JobRequirementAttachment]):
    """Repository for job requirement attachments."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, JobRequirementAttachment)

    async def create(
        self,
        tenant_id: UUID,
        job_requirement_id: UUID,
        *,
        file_name: str,
        file_key: str,
        content_type: str | None = None,
        file_size_bytes: int | None = None,
        created_by: UUID | None = None,
    ) -> JobRequirementAttachment:
        attachment = JobRequirementAttachment(
            tenant_id=tenant_id,
            job_requirement_id=job_requirement_id,
            file_name=file_name,
            file_key=file_key,
            content_type=content_type,
            file_size_bytes=file_size_bytes,
            created_by=created_by,
            updated_by=created_by,
        )
        return await self.add(attachment)
