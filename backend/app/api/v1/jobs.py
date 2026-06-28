"""Job requirement API endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Query, Request, UploadFile, status

from app.core.dependencies import CurrentUser, JobRequirementServiceDep
from app.schemas.auth import MessageResponse
from app.schemas.job_requirement import (
    JobAttachmentResponse,
    JobPriority,
    JobRequirementCreate,
    JobRequirementDetailResponse,
    JobRequirementListResponse,
    JobRequirementUpdate,
    JobStatus,
)

router = APIRouter(prefix="/jobs", tags=["Job Requirements"])

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10 MB


def _client_info(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.get(
    "",
    response_model=JobRequirementListResponse,
    summary="List job requirements",
)
async def list_jobs(
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
    search: str | None = Query(default=None, max_length=255),
    status: JobStatus | None = Query(default=None),
    client_id: UUID | None = Query(default=None),
    priority: JobPriority | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> JobRequirementListResponse:
    current_user.require_permission("jobs:read")
    return await job_service.list_jobs(
        current_user.tenant_id,
        search=search,
        status=status,
        client_id=client_id,
        priority=priority,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=JobRequirementDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job requirement",
)
async def create_job(
    data: JobRequirementCreate,
    request: Request,
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
) -> JobRequirementDetailResponse:
    current_user.require_permission("jobs:write")
    user_agent, ip_address = _client_info(request)
    return await job_service.create_job(
        current_user.tenant_id,
        data,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get(
    "/{job_id}",
    response_model=JobRequirementDetailResponse,
    summary="Get job requirement",
)
async def get_job(
    job_id: UUID,
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
) -> JobRequirementDetailResponse:
    current_user.require_permission("jobs:read")
    return await job_service.get_job(job_id, current_user.tenant_id)


@router.patch(
    "/{job_id}",
    response_model=JobRequirementDetailResponse,
    summary="Update job requirement",
)
async def update_job(
    job_id: UUID,
    data: JobRequirementUpdate,
    request: Request,
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
) -> JobRequirementDetailResponse:
    current_user.require_permission("jobs:write")
    user_agent, ip_address = _client_info(request)
    return await job_service.update_job(
        job_id,
        current_user.tenant_id,
        data,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.delete(
    "/{job_id}",
    response_model=MessageResponse,
    summary="Delete job requirement",
)
async def delete_job(
    job_id: UUID,
    request: Request,
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
) -> MessageResponse:
    current_user.require_permission("jobs:write")
    user_agent, ip_address = _client_info(request)
    await job_service.delete_job(
        job_id,
        current_user.tenant_id,
        current_user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return MessageResponse(message="Job requirement deleted successfully")


@router.post(
    "/{job_id}/attachments",
    response_model=JobAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload job attachment",
)
async def upload_attachment(
    job_id: UUID,
    current_user: CurrentUser,
    job_service: JobRequirementServiceDep,
    file: UploadFile = File(...),
) -> JobAttachmentResponse:
    current_user.require_permission("jobs:write")
    content = await file.read()
    if len(content) > MAX_ATTACHMENT_SIZE:
        from app.core.exceptions import ValidationError

        raise ValidationError("File size exceeds 10 MB limit")
    if not file.filename:
        from app.core.exceptions import ValidationError

        raise ValidationError("File name is required")

    return await job_service.upload_attachment(
        job_id,
        current_user.tenant_id,
        file.filename,
        content,
        file.content_type,
        current_user.user_id,
    )
