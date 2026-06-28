"""Dashboard Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DashboardStatCard(BaseModel):
    """Single metric card on the dashboard."""

    label: str
    value: int | float | str
    change_percent: float | None = None
    trend: str | None = None


class PipelineStage(BaseModel):
    """Recruitment pipeline stage with count."""

    stage: str
    label: str
    count: int
    color: str | None = None


class TodayInterviewItem(BaseModel):
    """Scheduled interview for today."""

    id: UUID
    candidate_name: str
    job_title: str
    client_name: str
    scheduled_at: datetime
    status: str


class RecentActivityItem(BaseModel):
    """Recent activity feed item."""

    id: UUID
    action: str
    resource_type: str
    description: str
    created_at: datetime


class ScoreSummary(BaseModel):
    """Average score summary for resumes or interviews."""

    average: float | None = None
    count: int = 0
    label: str


class DashboardOverviewResponse(BaseModel):
    """Complete dashboard overview payload."""

    stats: list[DashboardStatCard]
    pipeline: list[PipelineStage]
    todays_interviews: list[TodayInterviewItem] = Field(default_factory=list)
    recent_activity: list[RecentActivityItem] = Field(default_factory=list)
    resume_score: ScoreSummary
    interview_score: ScoreSummary
    clients_by_status: dict[str, int] = Field(default_factory=dict)
