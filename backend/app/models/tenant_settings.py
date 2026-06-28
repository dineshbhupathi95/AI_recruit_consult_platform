"""Per-tenant configuration overrides (AI provider, integrations, etc.)."""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import AuditMixin, UUIDPrimaryKeyMixin


class TenantSettings(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Tenant-scoped settings stored as JSON (overrides environment defaults)."""

    __tablename__ = "tenant_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
