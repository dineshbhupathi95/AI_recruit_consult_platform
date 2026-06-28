"""Candidate and pipeline API endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Query, Request, UploadFile, status
from fastapi.responses import Response

from app.core.dependencies import CandidatePipelineServiceDep, CurrentUser
from app.schemas.auth import MessageResponse
from app.schemas.candidate import (
    ApplicationCreate,
    ApplicationDetailResponse,
    ApplicationListResponse,
    BuildResumeRequest,
    CandidateCreate,
    CandidateListResponse,
    CandidateResponse,
    CandidateUpdate,
    InterviewAnswerRequest,
    InterviewQuestionResponse,
    RecruiterReviewRequest,
    ResumeBuildContextResponse,
    ResumeScoreResponse,
    ResumeVersionResponse,
    ScheduleInterviewRequest,
    ScreeningInterviewResponse,
    UpdateResumeVersionRequest,
)

router = APIRouter(tags=["Candidate Management"])


def _client_info(request: Request) -> tuple[str | None, str | None]:
    ua = request.headers.get("User-Agent")
    ip = request.client.host if request.client else None
    return ua, ip


@router.get("/candidates", response_model=CandidateListResponse)
async def list_candidates(
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CandidateListResponse:
    current_user.require_permission("candidates:read")
    return await service.list_candidates(current_user.tenant_id, search, page, page_size)


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    data: CandidateCreate,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> CandidateResponse:
    current_user.require_permission("candidates:write")
    return await service.create_candidate(current_user.tenant_id, data, current_user.user_id)


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> CandidateResponse:
    current_user.require_permission("candidates:read")
    return await service.get_candidate(candidate_id, current_user.tenant_id)


@router.patch("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: UUID,
    data: CandidateUpdate,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> CandidateResponse:
    current_user.require_permission("candidates:write")
    return await service.update_candidate(candidate_id, current_user.tenant_id, data, current_user.user_id)


@router.get("/applications", response_model=ApplicationListResponse)
async def list_applications(
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
    candidate_id: UUID | None = Query(default=None),
    job_requirement_id: UUID | None = Query(default=None),
    pipeline_stage: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApplicationListResponse:
    current_user.require_permission("candidates:read")
    return await service.list_applications(
        current_user.tenant_id, candidate_id, job_requirement_id, pipeline_stage, page, page_size
    )


@router.post("/applications", response_model=ApplicationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ApplicationDetailResponse:
    current_user.require_permission("candidates:write")
    return await service.create_application(
        current_user.tenant_id, data.candidate_id, data.job_requirement_id,
        data.recruiter_notes, current_user.user_id,
    )


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ApplicationDetailResponse:
    current_user.require_permission("candidates:read")
    return await service.get_application(application_id, current_user.tenant_id)


@router.post("/applications/{application_id}/resume", response_model=ApplicationDetailResponse)
async def upload_resume(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
    file: UploadFile = File(...),
) -> ApplicationDetailResponse:
    current_user.require_permission("candidates:write")
    content = await file.read()
    if not file.filename:
        from app.core.exceptions import ValidationError
        raise ValidationError("File name required")
    await service.upload_resume(
        application_id, current_user.tenant_id, file.filename, content, file.content_type, current_user.user_id
    )
    return await service.get_application(application_id, current_user.tenant_id)


@router.get("/applications/{application_id}/resume-build-context", response_model=ResumeBuildContextResponse)
async def get_resume_build_context(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ResumeBuildContextResponse:
    current_user.require_permission("candidates:read")
    return await service.get_resume_build_context(application_id, current_user.tenant_id)


@router.post("/applications/{application_id}/build-resume", response_model=ResumeVersionResponse)
async def build_resume(
    application_id: UUID,
    data: BuildResumeRequest,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ResumeVersionResponse:
    current_user.require_permission("candidates:write")
    return await service.build_resume(application_id, current_user.tenant_id, data, current_user.user_id)


@router.patch("/applications/{application_id}/resume-versions/{version_id}", response_model=ResumeVersionResponse)
async def update_resume_version(
    application_id: UUID,
    version_id: UUID,
    data: UpdateResumeVersionRequest,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ResumeVersionResponse:
    current_user.require_permission("candidates:write")
    return await service.update_resume_version(application_id, version_id, current_user.tenant_id, data, current_user.user_id)


@router.post("/applications/{application_id}/resume-versions/{version_id}/review", response_model=ResumeVersionResponse)
async def review_resume(
    application_id: UUID,
    version_id: UUID,
    data: RecruiterReviewRequest,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ResumeVersionResponse:
    current_user.require_permission("candidates:write")
    return await service.review_resume(application_id, version_id, current_user.tenant_id, data, current_user.user_id)


@router.post("/applications/{application_id}/score-resume", response_model=ResumeScoreResponse)
async def score_resume(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
    version_id: UUID | None = Query(default=None),
) -> ResumeScoreResponse:
    current_user.require_permission("candidates:write")
    return await service.score_resume(application_id, current_user.tenant_id, current_user.user_id, version_id)


@router.get("/applications/{application_id}/export/{format}")
async def export_resume(
    application_id: UUID,
    format: str,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
    version_id: UUID | None = Query(default=None),
) -> Response:
    current_user.require_permission("candidates:read")
    content, filename, media_type = await service.export_resume(application_id, current_user.tenant_id, format, version_id)
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.post("/applications/{application_id}/schedule-interview", response_model=ScreeningInterviewResponse)
async def schedule_interview(
    application_id: UUID,
    data: ScheduleInterviewRequest,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ScreeningInterviewResponse:
    current_user.require_permission("candidates:write")
    return await service.schedule_interview(application_id, current_user.tenant_id, data, current_user.user_id)


@router.post("/applications/{application_id}/interview/start", response_model=InterviewQuestionResponse)
async def start_interview(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> InterviewQuestionResponse:
    current_user.require_permission("candidates:write")
    return await service.start_interview(application_id, current_user.tenant_id)


@router.post("/applications/{application_id}/interview/answer", response_model=InterviewQuestionResponse)
async def submit_answer(
    application_id: UUID,
    data: InterviewAnswerRequest,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> InterviewQuestionResponse:
    current_user.require_permission("candidates:write")
    return await service.submit_interview_answer(application_id, current_user.tenant_id, data.answer)


@router.post("/applications/{application_id}/interview/complete", response_model=ScreeningInterviewResponse)
async def complete_interview(
    application_id: UUID,
    current_user: CurrentUser,
    service: CandidatePipelineServiceDep,
) -> ScreeningInterviewResponse:
    current_user.require_permission("candidates:write")
    return await service.complete_interview(application_id, current_user.tenant_id, current_user.user_id)
