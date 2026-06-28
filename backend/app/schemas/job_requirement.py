"""Job requirement Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class JobPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class JobStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class JobAttachmentResponse(BaseModel):
    """Job attachment metadata response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_requirement_id: UUID
    file_name: str
    file_key: str
    content_type: str | None
    file_size_bytes: int | None
    created_at: datetime


class JobRequirementCreate(BaseModel):
    """Create a job requirement."""

    client_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    hiring_manager_id: UUID | None = None
    client_location_id: UUID | None = None
    experience_min_years: int | None = Field(default=None, ge=0, le=50)
    experience_max_years: int | None = Field(default=None, ge=0, le=50)
    budget_min: Decimal | None = Field(default=None, ge=0)
    budget_max: Decimal | None = Field(default=None, ge=0)
    budget_currency: str = Field(default="USD", min_length=3, max_length=3)
    notice_period_days: int | None = Field(default=None, ge=0, le=365)
    location_text: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    priority: JobPriority = JobPriority.MEDIUM
    status: JobStatus = JobStatus.DRAFT
    description: str | None = Field(default=None, max_length=20000)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    @field_validator("required_skills", "preferred_skills")
    @classmethod
    def normalize_skills(cls, value: list[str]) -> list[str]:
        return [skill.strip() for skill in value if skill and skill.strip()]


class JobRequirementUpdate(BaseModel):
    """Update a job requirement."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    hiring_manager_id: UUID | None = None
    client_location_id: UUID | None = None
    experience_min_years: int | None = Field(default=None, ge=0, le=50)
    experience_max_years: int | None = Field(default=None, ge=0, le=50)
    budget_min: Decimal | None = Field(default=None, ge=0)
    budget_max: Decimal | None = Field(default=None, ge=0)
    budget_currency: str | None = Field(default=None, min_length=3, max_length=3)
    notice_period_days: int | None = Field(default=None, ge=0, le=365)
    location_text: str | None = Field(default=None, max_length=255)
    employment_type: EmploymentType | None = None
    priority: JobPriority | None = None
    status: JobStatus | None = None
    description: str | None = Field(default=None, max_length=20000)
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None

    @field_validator("required_skills", "preferred_skills")
    @classmethod
    def normalize_skills(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return [skill.strip() for skill in value if skill and skill.strip()]


class JobRequirementSummaryResponse(BaseModel):
    """Job list item."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    client_name: str
    title: str
    employment_type: EmploymentType
    priority: JobPriority
    status: JobStatus
    location_text: str | None
    experience_min_years: int | None
    experience_max_years: int | None
    required_skills_count: int = 0
    hiring_manager_name: str | None = None
    created_at: datetime
    updated_at: datetime


class JobRequirementDetailResponse(BaseModel):
    """Full job requirement detail."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    client_id: UUID
    client_name: str
    hiring_manager_id: UUID | None
    hiring_manager_name: str | None
    client_location_id: UUID | None
    client_location_name: str | None
    title: str
    experience_min_years: int | None
    experience_max_years: int | None
    budget_min: Decimal | None
    budget_max: Decimal | None
    budget_currency: str
    notice_period_days: int | None
    location_text: str | None
    employment_type: EmploymentType
    priority: JobPriority
    status: JobStatus
    description: str | None
    required_skills: list[str]
    preferred_skills: list[str]
    attachments: list[JobAttachmentResponse]
    created_at: datetime
    updated_at: datetime


class JobRequirementListResponse(BaseModel):
    """Paginated job requirement list."""

    items: list[JobRequirementSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
