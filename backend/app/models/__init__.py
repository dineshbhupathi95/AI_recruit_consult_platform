"""Import all models for Alembic autogenerate."""

from app.models.audit_log import AuditLog
from app.models.candidate import (
    Candidate,
    CandidateApplication,
    CandidateDocument,
    ParsedResume,
    ResumeScore,
    ResumeTemplate,
    ResumeVersion,
    ScreeningInterview,
)
from app.models.client import Client, ClientContact, ClientLocation, ClientNote
from app.models.job_requirement import JobRequirement, JobRequirementAttachment
from app.models.refresh_token import RefreshToken
from app.models.role import Permission, Role, role_permissions, user_roles
from app.models.tenant import Tenant
from app.models.tenant_settings import TenantSettings
from app.models.user import User

__all__ = [
    "AuditLog",
    "Candidate",
    "CandidateApplication",
    "CandidateDocument",
    "Client",
    "ClientContact",
    "ClientLocation",
    "ClientNote",
    "JobRequirement",
    "JobRequirementAttachment",
    "ParsedResume",
    "Permission",
    "RefreshToken",
    "ResumeScore",
    "ResumeTemplate",
    "ResumeVersion",
    "Role",
    "ScreeningInterview",
    "Tenant",
    "TenantSettings",
    "User",
    "role_permissions",
    "user_roles",
]
