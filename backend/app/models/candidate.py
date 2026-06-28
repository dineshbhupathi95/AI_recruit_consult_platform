"""Candidate and recruitment pipeline models."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
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
from app.models.base import AuditMixin, TimestampMixin, UUIDPrimaryKeyMixin


class PipelineStage(str, enum.Enum):
    SOURCED = "sourced"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SUBMITTED = "submitted"
    PLACED = "placed"


class ApplicationStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    PLACED = "placed"


class ParseStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeVersionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"
    REJECTED = "rejected"


class RecruiterReviewDecision(str, enum.Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_MORE_INTERVIEW = "needs_more_interview"
    NEEDS_RESUME_CHANGES = "needs_resume_changes"
    SUBMIT_TO_CLIENT = "submit_to_client"


class InterviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HireRecommendation(str, enum.Enum):
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    HOLD = "hold"
    REJECT = "reject"


class Candidate(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Candidate sourced by the recruitment consultancy."""

    __tablename__ = "candidates"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_ctc: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    expected_ctc: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    applications: Mapped[list["CandidateApplication"]] = relationship(
        "CandidateApplication", back_populates="candidate", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CandidateApplication(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Candidate pipeline for a specific job requirement."""

    __tablename__ = "candidate_applications"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_requirement_id", name="uq_candidate_job"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pipeline_stage: Mapped[PipelineStage] = mapped_column(
        Enum(PipelineStage, name="pipeline_stage", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PipelineStage.SOURCED,
        index=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ApplicationStatus.ACTIVE,
        index=True,
    )
    recruiter_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="applications")
    job_requirement: Mapped["JobRequirement"] = relationship("JobRequirement")
    documents: Mapped[list["CandidateDocument"]] = relationship(
        "CandidateDocument", back_populates="application", cascade="all, delete-orphan"
    )
    parsed_resume: Mapped["ParsedResume | None"] = relationship(
        "ParsedResume", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion", back_populates="application", cascade="all, delete-orphan",
        order_by="ResumeVersion.version_number",
    )
    resume_scores: Mapped[list["ResumeScore"]] = relationship(
        "ResumeScore", back_populates="application", cascade="all, delete-orphan"
    )
    screening_interview: Mapped["ScreeningInterview | None"] = relationship(
        "ScreeningInterview", back_populates="application", uselist=False, cascade="all, delete-orphan"
    )


class CandidateDocument(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Uploaded candidate document (resume, certificate, etc.)."""

    __tablename__ = "candidate_documents"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="resume", index=True)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_original_resume: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="documents")


class ParsedResume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """AI-parsed structured resume JSON — never store raw text only."""

    __tablename__ = "parsed_resumes"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_documents.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ParseStatus] = mapped_column(
        Enum(ParseStatus, name="parse_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ParseStatus.PENDING,
        index=True,
    )
    structured_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="parsed_resume")


class ResumeTemplate(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """HTML/CSS resume template for export."""

    __tablename__ = "resume_templates"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_template: Mapped[str] = mapped_column(Text, nullable=False)
    css_styles: Mapped[str] = mapped_column(Text, nullable=False, default="")
    config: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ResumeVersion(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Versioned AI-built resume JSON."""

    __tablename__ = "resume_versions"
    __table_args__ = (
        UniqueConstraint("application_id", "version_number", name="uq_resume_version_app_number"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resume_templates.id", ondelete="SET NULL"), nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ResumeVersionStatus] = mapped_column(
        Enum(ResumeVersionStatus, name="resume_version_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ResumeVersionStatus.DRAFT,
        index=True,
    )
    content_json: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    recruiter_review_decision: Mapped[RecruiterReviewDecision | None] = mapped_column(
        Enum(RecruiterReviewDecision, name="recruiter_review_decision", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    recruiter_review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="resume_versions")
    template: Mapped["ResumeTemplate | None"] = relationship("ResumeTemplate")


class ResumeScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ATS resume score for an application."""

    __tablename__ = "resume_scores"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    keyword_match: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    skill_match: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    experience_match: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    semantic_similarity: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    formatting_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    grammar_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    achievements_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    missing_keywords: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    suggestions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    improvement_areas: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )

    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="resume_scores")


class ScreeningInterview(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Scheduled AI screening interview."""

    __tablename__ = "screening_interviews"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus, name="interview_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=InterviewStatus.SCHEDULED,
        index=True,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=45)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    coding_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    behavioral: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    technical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="en")
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")
    interview_link: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    transcript: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    coding_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    communication_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    problem_solving_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    recommendation: Mapped[HireRecommendation | None] = mapped_column(
        Enum(HireRecommendation, name="hire_recommendation", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    evaluation_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="screening_interview")
