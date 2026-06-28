"""Job requirement business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.job_requirement import JobRequirement
from app.repositories.client_repository import (
    ClientContactRepository,
    ClientLocationRepository,
    ClientRepository,
)
from app.repositories.job_requirement_repository import (
    JobRequirementAttachmentRepository,
    JobRequirementRepository,
)
from app.schemas.job_requirement import (
    EmploymentType,
    JobAttachmentResponse,
    JobPriority,
    JobRequirementCreate,
    JobRequirementDetailResponse,
    JobRequirementListResponse,
    JobRequirementSummaryResponse,
    JobRequirementUpdate,
    JobStatus,
)
from app.services.audit_service import AuditService
from app.services.storage_service import StorageService

logger = get_logger(__name__)


class JobRequirementService:
    """Service layer for job requirement operations."""

    def __init__(
        self,
        job_repo: JobRequirementRepository,
        attachment_repo: JobRequirementAttachmentRepository,
        client_repo: ClientRepository,
        contact_repo: ClientContactRepository,
        location_repo: ClientLocationRepository,
        audit_service: AuditService,
        storage_service: StorageService,
    ) -> None:
        self._job_repo = job_repo
        self._attachment_repo = attachment_repo
        self._client_repo = client_repo
        self._contact_repo = contact_repo
        self._location_repo = location_repo
        self._audit_service = audit_service
        self._storage_service = storage_service

    @staticmethod
    def _enum_value(value) -> str:
        return value.value if hasattr(value, "value") else str(value)

    @staticmethod
    def _to_employment_type(value) -> EmploymentType:
        if isinstance(value, EmploymentType):
            return value
        return EmploymentType(value)

    @staticmethod
    def _to_priority(value) -> JobPriority:
        if isinstance(value, JobPriority):
            return value
        return JobPriority(value)

    @staticmethod
    def _to_status(value) -> JobStatus:
        if isinstance(value, JobStatus):
            return value
        return JobStatus(value)

    async def _validate_client_refs(
        self,
        tenant_id: UUID,
        client_id: UUID,
        hiring_manager_id: UUID | None,
        client_location_id: UUID | None,
    ) -> None:
        client = await self._client_repo.get_by_id_for_tenant(client_id, tenant_id)
        if client is None:
            raise NotFoundError("Client not found")

        if hiring_manager_id:
            contact = await self._contact_repo.get_by_id_for_client(
                hiring_manager_id, client_id, tenant_id
            )
            if contact is None:
                raise ValidationError("Hiring manager must belong to the selected client")

        if client_location_id:
            location = await self._location_repo.get_by_id_for_client(
                client_location_id, client_id, tenant_id
            )
            if location is None:
                raise ValidationError("Location must belong to the selected client")

    def _build_summary(self, job: JobRequirement) -> JobRequirementSummaryResponse:
        hiring_manager_name = None
        if job.hiring_manager and not job.hiring_manager.is_deleted:
            hiring_manager_name = job.hiring_manager.full_name

        return JobRequirementSummaryResponse(
            id=job.id,
            client_id=job.client_id,
            client_name=job.client.name if job.client else "",
            title=job.title,
            employment_type=self._to_employment_type(job.employment_type),
            priority=self._to_priority(job.priority),
            status=self._to_status(job.status),
            location_text=job.location_text,
            experience_min_years=job.experience_min_years,
            experience_max_years=job.experience_max_years,
            required_skills_count=len(job.required_skills or []),
            hiring_manager_name=hiring_manager_name,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    def _build_detail(self, job: JobRequirement) -> JobRequirementDetailResponse:
        hiring_manager_name = None
        if job.hiring_manager and not job.hiring_manager.is_deleted:
            hiring_manager_name = job.hiring_manager.full_name

        location_name = None
        if job.client_location and not job.client_location.is_deleted:
            location_name = job.client_location.name

        active_attachments = [a for a in job.attachments if not a.is_deleted]

        return JobRequirementDetailResponse(
            id=job.id,
            tenant_id=job.tenant_id,
            client_id=job.client_id,
            client_name=job.client.name if job.client else "",
            hiring_manager_id=job.hiring_manager_id,
            hiring_manager_name=hiring_manager_name,
            client_location_id=job.client_location_id,
            client_location_name=location_name,
            title=job.title,
            experience_min_years=job.experience_min_years,
            experience_max_years=job.experience_max_years,
            budget_min=job.budget_min,
            budget_max=job.budget_max,
            budget_currency=job.budget_currency,
            notice_period_days=job.notice_period_days,
            location_text=job.location_text,
            employment_type=self._to_employment_type(job.employment_type),
            priority=self._to_priority(job.priority),
            status=self._to_status(job.status),
            description=job.description,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
            attachments=[JobAttachmentResponse.model_validate(a) for a in active_attachments],
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    async def _get_job_or_raise(
        self,
        job_id: UUID,
        tenant_id: UUID,
        *,
        include_relations: bool = False,
    ) -> JobRequirement:
        job = await self._job_repo.get_by_id_for_tenant(
            job_id, tenant_id, include_relations=include_relations
        )
        if job is None:
            raise NotFoundError("Job requirement not found")
        return job

    async def list_jobs(
        self,
        tenant_id: UUID,
        *,
        search: str | None = None,
        status: JobStatus | None = None,
        client_id: UUID | None = None,
        priority: JobPriority | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> JobRequirementListResponse:
        jobs, total = await self._job_repo.list_for_tenant(
            tenant_id,
            search=search,
            status=status.value if status else None,
            client_id=client_id,
            priority=priority.value if priority else None,
            page=page,
            page_size=page_size,
        )
        return JobRequirementListResponse(
            items=[self._build_summary(j) for j in jobs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=self._job_repo.total_pages(total, page_size),
        )

    async def get_job(self, job_id: UUID, tenant_id: UUID) -> JobRequirementDetailResponse:
        job = await self._get_job_or_raise(job_id, tenant_id, include_relations=True)
        return self._build_detail(job)

    async def create_job(
        self,
        tenant_id: UUID,
        data: JobRequirementCreate,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> JobRequirementDetailResponse:
        if (
            data.experience_min_years is not None
            and data.experience_max_years is not None
            and data.experience_min_years > data.experience_max_years
        ):
            raise ValidationError("Minimum experience cannot exceed maximum experience")

        if (
            data.budget_min is not None
            and data.budget_max is not None
            and data.budget_min > data.budget_max
        ):
            raise ValidationError("Minimum budget cannot exceed maximum budget")

        await self._validate_client_refs(
            tenant_id,
            data.client_id,
            data.hiring_manager_id,
            data.client_location_id,
        )

        job = await self._job_repo.create(
            tenant_id,
            client_id=data.client_id,
            title=data.title,
            hiring_manager_id=data.hiring_manager_id,
            client_location_id=data.client_location_id,
            experience_min_years=data.experience_min_years,
            experience_max_years=data.experience_max_years,
            budget_min=data.budget_min,
            budget_max=data.budget_max,
            budget_currency=data.budget_currency,
            notice_period_days=data.notice_period_days,
            location_text=data.location_text,
            employment_type=data.employment_type.value,
            priority=data.priority.value,
            status=data.status.value,
            description=data.description,
            required_skills=data.required_skills,
            preferred_skills=data.preferred_skills,
            created_by=user_id,
        )

        await self._audit_service.log(
            tenant_id,
            "job.created",
            "job_requirement",
            user_id=user_id,
            resource_id=str(job.id),
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Created job requirement: {data.title}",
        )

        logger.info("job_created", job_id=str(job.id), tenant_id=str(tenant_id))
        return await self.get_job(job.id, tenant_id)

    async def update_job(
        self,
        job_id: UUID,
        tenant_id: UUID,
        data: JobRequirementUpdate,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> JobRequirementDetailResponse:
        job = await self._get_job_or_raise(job_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise ValidationError("No fields provided for update")

        hiring_manager_id = update_data.get("hiring_manager_id", job.hiring_manager_id)
        client_location_id = update_data.get("client_location_id", job.client_location_id)
        await self._validate_client_refs(
            tenant_id,
            job.client_id,
            hiring_manager_id,
            client_location_id,
        )

        exp_min = update_data.get("experience_min_years", job.experience_min_years)
        exp_max = update_data.get("experience_max_years", job.experience_max_years)
        if exp_min is not None and exp_max is not None and exp_min > exp_max:
            raise ValidationError("Minimum experience cannot exceed maximum experience")

        budget_min = update_data.get("budget_min", job.budget_min)
        budget_max = update_data.get("budget_max", job.budget_max)
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise ValidationError("Minimum budget cannot exceed maximum budget")

        changes: dict[str, dict[str, str | None]] = {}
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            old_value = getattr(job, field)
            if old_value != value:
                changes[field] = {
                    "old": str(old_value) if old_value is not None else None,
                    "new": str(value) if value is not None else None,
                }
                setattr(job, field, value)

        job.updated_by = user_id
        await self._job_repo._session.flush()

        await self._audit_service.log(
            tenant_id,
            "job.updated",
            "job_requirement",
            user_id=user_id,
            resource_id=str(job_id),
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            description=f"Updated job requirement: {job.title}",
        )

        return await self.get_job(job_id, tenant_id)

    async def delete_job(
        self,
        job_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        job = await self._get_job_or_raise(job_id, tenant_id)
        await self._job_repo.soft_delete(job, deleted_by=user_id)

        await self._audit_service.log(
            tenant_id,
            "job.deleted",
            "job_requirement",
            user_id=user_id,
            resource_id=str(job_id),
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Deleted job requirement: {job.title}",
        )

    async def upload_attachment(
        self,
        job_id: UUID,
        tenant_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
        user_id: UUID,
    ) -> JobAttachmentResponse:
        job = await self._get_job_or_raise(job_id, tenant_id)
        object_key, file_size = self._storage_service.upload_job_attachment(
            tenant_id,
            job.id,
            file_name,
            content,
            content_type,
        )
        attachment = await self._attachment_repo.create(
            tenant_id,
            job.id,
            file_name=file_name,
            file_key=object_key,
            content_type=content_type,
            file_size_bytes=file_size,
            created_by=user_id,
        )

        await self._audit_service.log(
            tenant_id,
            "job.attachment.uploaded",
            "job_requirement_attachment",
            user_id=user_id,
            resource_id=str(attachment.id),
            description=f"Uploaded attachment {file_name} to job {job.title}",
        )
        return JobAttachmentResponse.model_validate(attachment)
