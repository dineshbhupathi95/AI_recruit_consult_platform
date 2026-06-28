"""Dashboard aggregation business logic."""

from uuid import UUID

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.candidate_repository import (
    CandidateApplicationRepository,
    CandidateRepository,
    ResumeScoreRepository,
    ScreeningInterviewRepository,
)
from app.repositories.client_repository import ClientContactRepository, ClientRepository
from app.repositories.job_requirement_repository import JobRequirementRepository
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    DashboardStatCard,
    PipelineStage,
    RecentActivityItem,
    ScoreSummary,
    TodayInterviewItem,
)


class DashboardService:
    """Service layer for dashboard metrics and overview."""

    PIPELINE_STAGES = [
        ("sourced", "Sourced", "bg-blue-500"),
        ("screening", "Screening", "bg-yellow-500"),
        ("interview", "Interview", "bg-purple-500"),
        ("submitted", "Submitted", "bg-green-500"),
        ("placed", "Placed", "bg-emerald-600"),
    ]

    def __init__(
        self,
        client_repo: ClientRepository,
        contact_repo: ClientContactRepository,
        audit_repo: AuditLogRepository,
        job_repo: JobRequirementRepository,
        candidate_repo: CandidateRepository,
        application_repo: CandidateApplicationRepository,
        score_repo: ResumeScoreRepository,
        interview_repo: ScreeningInterviewRepository,
    ) -> None:
        self._client_repo = client_repo
        self._contact_repo = contact_repo
        self._audit_repo = audit_repo
        self._job_repo = job_repo
        self._candidate_repo = candidate_repo
        self._application_repo = application_repo
        self._score_repo = score_repo
        self._interview_repo = interview_repo

    async def get_overview(self, tenant_id: UUID) -> DashboardOverviewResponse:
        """Build dashboard overview with available metrics."""
        total_clients = await self._client_repo.count_total(tenant_id)
        clients_by_status = await self._client_repo.count_by_status(tenant_id)
        active_clients = clients_by_status.get("active", 0)
        hiring_managers = await self._contact_repo.count_hiring_managers(tenant_id)
        active_requirements = await self._job_repo.count_active(tenant_id)
        total_candidates = await self._candidate_repo.count_total(tenant_id)
        pending_interviews = await self._interview_repo.count_pending(tenant_id)
        pipeline_counts = await self._application_repo.count_by_pipeline_stage(tenant_id)
        resume_avg, resume_count = await self._score_repo.average_score(tenant_id)
        interview_avg, interview_count = await self._interview_repo.average_interview_score(tenant_id)

        stats = [
            DashboardStatCard(label="Active Clients", value=active_clients),
            DashboardStatCard(label="Total Clients", value=total_clients),
            DashboardStatCard(label="Active Requirements", value=active_requirements),
            DashboardStatCard(label="Candidates", value=total_candidates),
            DashboardStatCard(label="Pending Interviews", value=pending_interviews),
            DashboardStatCard(label="Hiring Managers", value=hiring_managers),
        ]

        pipeline = [
            PipelineStage(
                stage=stage,
                label=label,
                count=pipeline_counts.get(stage, 0),
                color=color,
            )
            for stage, label, color in self.PIPELINE_STAGES
        ]

        recent_logs = await self._audit_repo.list_recent_for_tenant(tenant_id, limit=10)
        recent_activity = [
            RecentActivityItem(
                id=log.id,
                action=log.action,
                resource_type=log.resource_type,
                description=log.description or f"{log.action} on {log.resource_type}",
                created_at=log.created_at,
            )
            for log in recent_logs
        ]

        todays = await self._interview_repo.get_todays_interviews(tenant_id)
        todays_interviews = []
        for interview in todays:
            app = interview.application
            candidate_name = app.candidate.full_name if app and app.candidate else "Unknown"
            job_title = app.job_requirement.title if app and app.job_requirement else ""
            client_name = ""
            if app and app.job_requirement and app.job_requirement.client:
                client_name = app.job_requirement.client.name
            if interview.scheduled_at:
                todays_interviews.append(
                    TodayInterviewItem(
                        id=interview.id,
                        candidate_name=candidate_name,
                        job_title=job_title,
                        client_name=client_name,
                        scheduled_at=interview.scheduled_at,
                        status=interview.status.value,
                    )
                )

        return DashboardOverviewResponse(
            stats=stats,
            pipeline=pipeline,
            todays_interviews=todays_interviews,
            recent_activity=recent_activity,
            resume_score=ScoreSummary(average=resume_avg, count=resume_count, label="Avg Resume Score"),
            interview_score=ScoreSummary(average=interview_avg, count=interview_count, label="Avg Interview Score"),
            clients_by_status=clients_by_status,
        )
