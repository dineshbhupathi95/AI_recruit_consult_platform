"""Job requirement models."""

import enum
import uuid
from decimal import Decimal

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditMixin, UUIDPrimaryKeyMixin


class EmploymentType(str, enum.Enum):
    """Employment arrangement for a job."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class JobPriority(str, enum.Enum):
    """Recruitment priority level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class JobStatus(str, enum.Enum):
    """Job requirement lifecycle status."""

    DRAFT = "draft"
    OPEN = "open"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class JobRequirement(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Client job requirement / open position."""

    __tablename__ = "job_requirements"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hiring_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("client_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("client_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    experience_min_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_max_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_min: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    budget_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType, name="employment_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EmploymentType.FULL_TIME,
        index=True,
    )
    priority: Mapped[JobPriority] = mapped_column(
        Enum(JobPriority, name="job_priority", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=JobPriority.MEDIUM,
        index=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=JobStatus.DRAFT,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_skills: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )
    preferred_skills: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )

    client: Mapped["Client"] = relationship("Client", back_populates="job_requirements")
    hiring_manager: Mapped["ClientContact | None"] = relationship("ClientContact")
    client_location: Mapped["ClientLocation | None"] = relationship("ClientLocation")
    attachments: Mapped[list["JobRequirementAttachment"]] = relationship(
        "JobRequirementAttachment",
        back_populates="job_requirement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<JobRequirement id={self.id} title={self.title}>"


class JobRequirementAttachment(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """File attachment metadata for a job requirement."""

    __tablename__ = "job_requirement_attachments"
    __table_args__ = (
        UniqueConstraint("job_requirement_id", "file_key", name="uq_job_attachments_job_file_key"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    job_requirement: Mapped["JobRequirement"] = relationship(
        "JobRequirement",
        back_populates="attachments",
    )

    def __repr__(self) -> str:
        return f"<JobRequirementAttachment id={self.id} file={self.file_name}>"
