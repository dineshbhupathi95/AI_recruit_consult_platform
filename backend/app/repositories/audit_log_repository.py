"""Audit log data access layer."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit trail entries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def create(
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
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_=metadata,
            changes=changes,
            description=description,
        )
        return await self.add(entry)

    async def list_recent_for_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int = 10,
    ) -> list[AuditLog]:
        """Fetch recent audit entries for dashboard activity feed."""
        query = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
