"""Pydantic schemas for candidate management and pipeline."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.resume_template import ResumeTemplateSummary


class PipelineStage(str, Enum):
    SOURCED = "sourced"
    SCREENING = "screening"
    INTERVIEW = "interview"
    SUBMITTED = "submitted"
    PLACED = "placed"


class ApplicationStatus(str, Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    PLACED = "placed"


class ParseStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeVersionStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"
    REJECTED = "rejected"


class RecruiterReviewDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_MORE_INTERVIEW = "needs_more_interview"
    NEEDS_RESUME_CHANGES = "needs_resume_changes"
    SUBMIT_TO_CLIENT = "submit_to_client"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HireRecommendation(str, Enum):
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    HOLD = "hold"
    REJECT = "reject"


class CandidateCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    linkedin_url: str | None = Field(default=None, max_length=512)
    github_url: str | None = Field(default=None, max_length=512)
    portfolio_url: str | None = Field(default=None, max_length=512)
    current_company: str | None = Field(default=None, max_length=255)
    current_ctc: Decimal | None = Field(default=None, ge=0)
    expected_ctc: Decimal | None = Field(default=None, ge=0)
    notice_period_days: int | None = Field(default=None, ge=0, le=365)
    notes: str | None = Field(default=None, max_length=5000)
    job_requirement_id: UUID | None = None


class CandidateUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    current_company: str | None = None
    current_ctc: Decimal | None = None
    expected_ctc: Decimal | None = None
    notice_period_days: int | None = None
    notes: str | None = None


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    full_name: str
    email: str | None
    phone: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    current_company: str | None
    current_ctc: Decimal | None
    expected_ctc: Decimal | None
    notice_period_days: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CandidateListResponse(BaseModel):
    items: list[CandidateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationCreate(BaseModel):
    candidate_id: UUID
    job_requirement_id: UUID
    recruiter_notes: str | None = None


class ParsedResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    status: ParseStatus
    structured_data: dict[str, Any] | None
    error_message: str | None
    parsed_at: datetime | None


class ResumeVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    version_number: int
    status: ResumeVersionStatus
    template_id: UUID | None = None
    template_name: str | None = None
    content_json: dict[str, Any]
    recruiter_review_decision: RecruiterReviewDecision | None
    recruiter_review_notes: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ResumeScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    resume_version_id: UUID | None
    overall_score: Decimal
    keyword_match: Decimal | None
    skill_match: Decimal | None
    experience_match: Decimal | None
    semantic_similarity: Decimal | None
    formatting_score: Decimal | None
    grammar_score: Decimal | None
    achievements_score: Decimal | None
    missing_keywords: list[str]
    suggestions: list[str]
    improvement_areas: list[str]
    created_at: datetime


class ScreeningInterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    status: InterviewStatus
    scheduled_at: datetime | None
    duration_minutes: int
    difficulty: str
    coding_required: bool
    behavioral: bool
    technical: bool
    language: str
    timezone: str
    interview_link: str | None
    transcript: list[dict[str, Any]]
    summary: str | None
    technical_score: Decimal | None
    coding_score: Decimal | None
    communication_score: Decimal | None
    confidence_score: Decimal | None
    problem_solving_score: Decimal | None
    recommendation: HireRecommendation | None
    completed_at: datetime | None


class ApplicationSummaryResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    candidate_name: str
    job_requirement_id: UUID
    job_title: str
    client_name: str
    pipeline_stage: PipelineStage
    status: ApplicationStatus
    has_parsed_resume: bool
    resume_version_count: int
    latest_resume_version_id: UUID | None = None
    latest_built_resume_status: ResumeVersionStatus | None = None
    latest_score: Decimal | None
    interview_status: InterviewStatus | None
    interview_overall_score: Decimal | None = None
    created_at: datetime
    updated_at: datetime


class ApplicationDetailResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    candidate_id: UUID
    candidate: CandidateResponse
    job_requirement_id: UUID
    job_title: str
    client_name: str
    job_description: str | None
    job_experience_min_years: int | None = None
    job_experience_max_years: int | None = None
    pipeline_stage: PipelineStage
    status: ApplicationStatus
    recruiter_notes: str | None
    parsed_resume: ParsedResumeResponse | None
    resume_versions: list[ResumeVersionResponse]
    resume_scores: list[ResumeScoreResponse]
    screening_interview: ScreeningInterviewResponse | None
    created_at: datetime
    updated_at: datetime


class ApplicationListResponse(BaseModel):
    items: list[ApplicationSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BuildResumeRequest(BaseModel):
    recruiter_notes: str | None = None
    template_id: UUID | None = None
    gap_strategy: str = Field(default="none", max_length=50)
    target_total_experience_years: float | None = Field(default=None, ge=0, le=50)
    summary: str | None = None
    skills: list[str] | None = None
    experience: list[dict[str, Any]] | None = None
    education: list[dict[str, Any]] | None = None
    training_entry: dict[str, Any] | None = None


class TimelineGapResponse(BaseModel):
    label: str
    from_date: str
    to_date: str
    months: int
    suggestion: str


class GapStrategyOption(BaseModel):
    id: str
    label: str
    description: str


class ResumeBuildContextResponse(BaseModel):
    job_experience_min_years: int | None
    job_experience_max_years: int | None
    candidate_total_experience_years: float
    experience_shortfall_years: float | None
    timeline_gaps: list[TimelineGapResponse]
    gap_strategy_options: list[GapStrategyOption]
    recommendations: list[str]
    default_summary: str | None
    default_skills: list[str]
    default_experience: list[dict[str, Any]]
    default_education: list[dict[str, Any]]
    templates: list[ResumeTemplateSummary] = []
    default_template_id: UUID | None = None


class UpdateResumeVersionRequest(BaseModel):
    content_json: dict[str, Any]


class RecruiterReviewRequest(BaseModel):
    decision: RecruiterReviewDecision
    notes: str | None = None


class ScheduleInterviewRequest(BaseModel):
    scheduled_at: datetime | None = None
    duration_minutes: int = Field(default=45, ge=15, le=180)
    difficulty: str = Field(default="medium", max_length=50)
    coding_required: bool = False
    behavioral: bool = True
    technical: bool = True
    language: str = Field(default="en", max_length=50)
    timezone: str = Field(default="UTC", max_length=100)


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=10000)


class InterviewQuestionResponse(BaseModel):
    question: str
    interview_status: InterviewStatus
    question_number: int
    question_type: str = "mcq"
    options: list[dict[str, str]] = Field(default_factory=list)
    phase_label: str | None = None
    total_questions: int = 18
    is_complete: bool = False


class MessageResponse(BaseModel):
    message: str
