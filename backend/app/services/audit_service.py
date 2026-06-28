"""Audit logging service."""

from typing import Any
from uuid import UUID

from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Service for recording audit trail entries."""

    def __init__(self, audit_repo: AuditLogRepository) -> None:
        self._audit_repo = audit_repo

    async def log(
        self,
        tenant_id: UUID,
        action: str,
        resource_type: str,
        *,
        user_id: UUID | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
        changes: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> None:
        """Record an audit log entry."""
        await self._audit_repo.create(
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
            changes=changes,
            description=description,
        )
