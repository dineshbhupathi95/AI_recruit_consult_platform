"""FastAPI dependency injection providers."""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token, validate_token_type
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.client_repository import (
    ClientContactRepository,
    ClientLocationRepository,
    ClientNoteRepository,
    ClientRepository,
)
from app.repositories.candidate_repository import (
    CandidateApplicationRepository,
    CandidateDocumentRepository,
    CandidateRepository,
    ParsedResumeRepository,
    ResumeScoreRepository,
    ResumeVersionRepository,
    ResumeTemplateRepository,
    ScreeningInterviewRepository,
)
from app.repositories.job_requirement_repository import (
    JobRequirementAttachmentRepository,
    JobRequirementRepository,
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.tenant_settings_repository import TenantSettingsRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.candidate_pipeline_service import CandidatePipelineService
from app.services.client_service import ClientService
from app.services.dashboard_service import DashboardService
from app.services.job_requirement_service import JobRequirementService
from app.services.resume_export_service import ResumeExportService
from app.services.resume_template_service import ResumeTemplateService
from app.services.storage_service import StorageService
from app.services.tenant_settings_service import TenantSettingsService

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: DbSession) -> UserRepository:
    return UserRepository(session)


def get_tenant_repository(session: DbSession) -> TenantRepository:
    return TenantRepository(session)


def get_role_repository(session: DbSession) -> RoleRepository:
    return RoleRepository(session)


def get_refresh_token_repository(session: DbSession) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    tenant_repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
) -> AuthService:
    return AuthService(user_repo, tenant_repo, role_repo, refresh_token_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_audit_log_repository(session: DbSession) -> AuditLogRepository:
    return AuditLogRepository(session)


def get_client_repository(session: DbSession) -> ClientRepository:
    return ClientRepository(session)


def get_client_contact_repository(session: DbSession) -> ClientContactRepository:
    return ClientContactRepository(session)


def get_client_location_repository(session: DbSession) -> ClientLocationRepository:
    return ClientLocationRepository(session)


def get_client_note_repository(session: DbSession) -> ClientNoteRepository:
    return ClientNoteRepository(session)


def get_audit_service(
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> AuditService:
    return AuditService(audit_repo)


def get_client_service(
    client_repo: Annotated[ClientRepository, Depends(get_client_repository)],
    contact_repo: Annotated[ClientContactRepository, Depends(get_client_contact_repository)],
    location_repo: Annotated[ClientLocationRepository, Depends(get_client_location_repository)],
    note_repo: Annotated[ClientNoteRepository, Depends(get_client_note_repository)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
) -> ClientService:
    return ClientService(client_repo, contact_repo, location_repo, note_repo, audit_service)


def get_job_requirement_repository(session: DbSession) -> JobRequirementRepository:
    return JobRequirementRepository(session)


def get_job_attachment_repository(session: DbSession) -> JobRequirementAttachmentRepository:
    return JobRequirementAttachmentRepository(session)


def get_storage_service() -> StorageService:
    return StorageService()


def get_job_requirement_service(
    job_repo: Annotated[JobRequirementRepository, Depends(get_job_requirement_repository)],
    attachment_repo: Annotated[
        JobRequirementAttachmentRepository, Depends(get_job_attachment_repository)
    ],
    client_repo: Annotated[ClientRepository, Depends(get_client_repository)],
    contact_repo: Annotated[ClientContactRepository, Depends(get_client_contact_repository)],
    location_repo: Annotated[ClientLocationRepository, Depends(get_client_location_repository)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> JobRequirementService:
    return JobRequirementService(
        job_repo,
        attachment_repo,
        client_repo,
        contact_repo,
        location_repo,
        audit_service,
        storage_service,
    )


def get_candidate_repository(session: DbSession) -> CandidateRepository:
    return CandidateRepository(session)


def get_application_repository(session: DbSession) -> CandidateApplicationRepository:
    return CandidateApplicationRepository(session)


def get_candidate_document_repository(session: DbSession) -> CandidateDocumentRepository:
    return CandidateDocumentRepository(session)


def get_parsed_resume_repository(session: DbSession) -> ParsedResumeRepository:
    return ParsedResumeRepository(session)


def get_resume_version_repository(session: DbSession) -> ResumeVersionRepository:
    return ResumeVersionRepository(session)


def get_resume_score_repository(session: DbSession) -> ResumeScoreRepository:
    return ResumeScoreRepository(session)


def get_screening_interview_repository(session: DbSession) -> ScreeningInterviewRepository:
    return ScreeningInterviewRepository(session)


def get_resume_export_service() -> ResumeExportService:
    return ResumeExportService()


def get_tenant_settings_repository(session: DbSession) -> TenantSettingsRepository:
    return TenantSettingsRepository(session)


def get_tenant_settings_service(
    repo: Annotated[TenantSettingsRepository, Depends(get_tenant_settings_repository)],
) -> TenantSettingsService:
    return TenantSettingsService(repo)


def get_dashboard_service(
    client_repo: Annotated[ClientRepository, Depends(get_client_repository)],
    contact_repo: Annotated[ClientContactRepository, Depends(get_client_contact_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    job_repo: Annotated[JobRequirementRepository, Depends(get_job_requirement_repository)],
    candidate_repo: Annotated[CandidateRepository, Depends(get_candidate_repository)],
    application_repo: Annotated[CandidateApplicationRepository, Depends(get_application_repository)],
    score_repo: Annotated[ResumeScoreRepository, Depends(get_resume_score_repository)],
    interview_repo: Annotated[ScreeningInterviewRepository, Depends(get_screening_interview_repository)],
) -> DashboardService:
    return DashboardService(
        client_repo, contact_repo, audit_repo, job_repo,
        candidate_repo, application_repo, score_repo, interview_repo,
    )


def get_resume_template_repository(session: DbSession) -> ResumeTemplateRepository:
    return ResumeTemplateRepository(session)


def get_resume_template_service(
    template_repo: Annotated[ResumeTemplateRepository, Depends(get_resume_template_repository)],
    export_service: Annotated[ResumeExportService, Depends(get_resume_export_service)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    settings_service: Annotated[TenantSettingsService, Depends(get_tenant_settings_service)],
) -> ResumeTemplateService:
    return ResumeTemplateService(template_repo, export_service, storage_service, settings_service)


def get_candidate_pipeline_service(
    candidate_repo: Annotated[CandidateRepository, Depends(get_candidate_repository)],
    application_repo: Annotated[CandidateApplicationRepository, Depends(get_application_repository)],
    document_repo: Annotated[CandidateDocumentRepository, Depends(get_candidate_document_repository)],
    parsed_repo: Annotated[ParsedResumeRepository, Depends(get_parsed_resume_repository)],
    version_repo: Annotated[ResumeVersionRepository, Depends(get_resume_version_repository)],
    score_repo: Annotated[ResumeScoreRepository, Depends(get_resume_score_repository)],
    interview_repo: Annotated[ScreeningInterviewRepository, Depends(get_screening_interview_repository)],
    job_repo: Annotated[JobRequirementRepository, Depends(get_job_requirement_repository)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    export_service: Annotated[ResumeExportService, Depends(get_resume_export_service)],
    settings_service: Annotated[TenantSettingsService, Depends(get_tenant_settings_service)],
    template_service: Annotated[ResumeTemplateService, Depends(get_resume_template_service)],
) -> CandidatePipelineService:
    return CandidatePipelineService(
        candidate_repo, application_repo, document_repo, parsed_repo,
        version_repo, score_repo, interview_repo, job_repo,
        audit_service, storage_service, export_service, settings_service,
        template_service,
    )


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]
DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
JobRequirementServiceDep = Annotated[JobRequirementService, Depends(get_job_requirement_service)]
CandidatePipelineServiceDep = Annotated[CandidatePipelineService, Depends(get_candidate_pipeline_service)]
ResumeTemplateServiceDep = Annotated[ResumeTemplateService, Depends(get_resume_template_service)]
TenantSettingsServiceDep = Annotated[TenantSettingsService, Depends(get_tenant_settings_service)]
AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


class CurrentUserContext:
    """Authenticated user context extracted from JWT."""

    def __init__(
        self,
        user_id: UUID,
        tenant_id: UUID,
        email: str,
        roles: list[str],
        permissions: list[str],
    ) -> None:
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email
        self.roles = roles
        self.permissions = permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or "admin" in self.roles

    def require_permission(self, permission: str) -> None:
        if not self.has_permission(permission):
            raise ForbiddenError(f"Missing required permission: {permission}")


async def get_current_user_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> CurrentUserContext:
    """Extract and validate the current user from the JWT access token."""
    if credentials is None:
        raise UnauthorizedError("Authentication credentials required")

    try:
        payload = decode_token(credentials.credentials)
        validate_token_type(payload, "access")
        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
    except (JWTError, KeyError, ValueError) as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    user = await user_repo.get_by_id(user_id)
    if user is None or user.is_deleted or not user.is_active:
        raise UnauthorizedError("User account is inactive or not found")

    if user.tenant_id != tenant_id:
        raise UnauthorizedError("Invalid tenant context")

    return CurrentUserContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
    )


CurrentUser = Annotated[CurrentUserContext, Depends(get_current_user_context)]


def require_permissions(*required_permissions: str) -> Callable[..., CurrentUserContext]:
    """Dependency factory that enforces one or more permissions."""

    async def _dependency(current_user: CurrentUser) -> CurrentUserContext:
        for permission in required_permissions:
            current_user.require_permission(permission)
        return current_user

    return _dependency


async def get_request_id(x_request_id: Annotated[str | None, Header()] = None) -> str:
    """Return request ID from header or generate a placeholder."""
    return x_request_id or "unknown"
