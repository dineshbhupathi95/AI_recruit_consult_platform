"""Candidate pipeline data access."""

from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import (
    Candidate,
    CandidateApplication,
    CandidateDocument,
    ParsedResume,
    PipelineStage,
    ResumeScore,
    ResumeTemplate,
    ResumeVersion,
    ScreeningInterview,
)
from app.models.job_requirement import JobRequirement
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Candidate)

    async def get_by_id_for_tenant(self, candidate_id: UUID, tenant_id: UUID) -> Candidate | None:
        result = await self._session.execute(
            select(Candidate).where(
                Candidate.id == candidate_id,
                Candidate.tenant_id == tenant_id,
                Candidate.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_tenant(
        self, tenant_id: UUID, *, search: str | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[Candidate], int]:
        base = select(Candidate).where(Candidate.tenant_id == tenant_id, Candidate.is_deleted.is_(False))
        if search:
            pattern = f"%{search}%"
            base = base.where(
                or_(
                    Candidate.first_name.ilike(pattern),
                    Candidate.last_name.ilike(pattern),
                    Candidate.email.ilike(pattern),
                    Candidate.current_company.ilike(pattern),
                )
            )
        total = (await self._session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        query = base.order_by(Candidate.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await self._session.execute(query)).scalars().all())
        return items, total

    async def create(self, tenant_id: UUID, **kwargs) -> Candidate:
        candidate = Candidate(tenant_id=tenant_id, **kwargs)
        return await self.add(candidate)

    async def soft_delete(self, candidate: Candidate, deleted_by: UUID | None = None) -> Candidate:
        candidate.is_deleted = True
        candidate.deleted_at = datetime.now(timezone.utc)
        candidate.updated_by = deleted_by
        await self._session.flush()
        return candidate

    async def count_total(self, tenant_id: UUID) -> int:
        q = select(func.count(Candidate.id)).where(
            Candidate.tenant_id == tenant_id, Candidate.is_deleted.is_(False)
        )
        return (await self._session.execute(q)).scalar_one()

    @staticmethod
    def total_pages(total: int, page_size: int) -> int:
        return 0 if total == 0 else ceil(total / page_size)


class CandidateApplicationRepository(BaseRepository[CandidateApplication]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CandidateApplication)

    async def get_by_id_for_tenant(
        self, application_id: UUID, tenant_id: UUID, *, full: bool = False
    ) -> CandidateApplication | None:
        query = select(CandidateApplication).where(
            CandidateApplication.id == application_id,
            CandidateApplication.tenant_id == tenant_id,
            CandidateApplication.is_deleted.is_(False),
        )
        if full:
            query = query.options(
                selectinload(CandidateApplication.candidate),
                selectinload(CandidateApplication.job_requirement).selectinload(JobRequirement.client),
                selectinload(CandidateApplication.documents),
                selectinload(CandidateApplication.parsed_resume),
                selectinload(CandidateApplication.resume_versions),
                selectinload(CandidateApplication.resume_scores),
                selectinload(CandidateApplication.screening_interview),
            )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        candidate_id: UUID | None = None,
        job_requirement_id: UUID | None = None,
        pipeline_stage: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[CandidateApplication], int]:
        base = select(CandidateApplication).where(
            CandidateApplication.tenant_id == tenant_id,
            CandidateApplication.is_deleted.is_(False),
        )
        if candidate_id:
            base = base.where(CandidateApplication.candidate_id == candidate_id)
        if job_requirement_id:
            base = base.where(CandidateApplication.job_requirement_id == job_requirement_id)
        if pipeline_stage:
            base = base.where(CandidateApplication.pipeline_stage == pipeline_stage)

        total = (await self._session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        query = (
            base.options(
                selectinload(CandidateApplication.candidate),
                selectinload(CandidateApplication.job_requirement).selectinload(JobRequirement.client),
                selectinload(CandidateApplication.parsed_resume),
                selectinload(CandidateApplication.resume_versions),
                selectinload(CandidateApplication.resume_scores),
                selectinload(CandidateApplication.screening_interview),
            )
            .order_by(CandidateApplication.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list((await self._session.execute(query)).scalars().all()), total

    async def create(self, tenant_id: UUID, candidate_id: UUID, job_requirement_id: UUID, **kwargs) -> CandidateApplication:
        app = CandidateApplication(
            tenant_id=tenant_id,
            candidate_id=candidate_id,
            job_requirement_id=job_requirement_id,
            **kwargs,
        )
        return await self.add(app)

    async def count_by_pipeline_stage(self, tenant_id: UUID) -> dict[str, int]:
        q = (
            select(CandidateApplication.pipeline_stage, func.count(CandidateApplication.id))
            .where(CandidateApplication.tenant_id == tenant_id, CandidateApplication.is_deleted.is_(False))
            .group_by(CandidateApplication.pipeline_stage)
        )
        result = await self._session.execute(q)
        return {str(row[0].value): row[1] for row in result.all()}


class CandidateDocumentRepository(BaseRepository[CandidateDocument]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CandidateDocument)

    async def create(self, tenant_id: UUID, application_id: UUID, **kwargs) -> CandidateDocument:
        doc = CandidateDocument(tenant_id=tenant_id, application_id=application_id, **kwargs)
        return await self.add(doc)


class ParsedResumeRepository(BaseRepository[ParsedResume]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ParsedResume)

    async def get_by_application(self, application_id: UUID, tenant_id: UUID) -> ParsedResume | None:
        result = await self._session.execute(
            select(ParsedResume).where(
                ParsedResume.application_id == application_id,
                ParsedResume.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_for_application(self, tenant_id: UUID, application_id: UUID, **kwargs) -> ParsedResume:
        existing = await self.get_by_application(application_id, tenant_id)
        if existing:
            for k, v in kwargs.items():
                setattr(existing, k, v)
            await self._session.flush()
            return existing
        record = ParsedResume(tenant_id=tenant_id, application_id=application_id, **kwargs)
        return await self.add(record)


class ResumeVersionRepository(BaseRepository[ResumeVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResumeVersion)

    async def get_by_id_for_application(
        self, version_id: UUID, application_id: UUID, tenant_id: UUID
    ) -> ResumeVersion | None:
        result = await self._session.execute(
            select(ResumeVersion).where(
                ResumeVersion.id == version_id,
                ResumeVersion.application_id == application_id,
                ResumeVersion.tenant_id == tenant_id,
                ResumeVersion.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def next_version_number(self, application_id: UUID) -> int:
        q = select(func.max(ResumeVersion.version_number)).where(
            ResumeVersion.application_id == application_id
        )
        max_v = (await self._session.execute(q)).scalar_one()
        return (max_v or 0) + 1

    async def create(self, tenant_id: UUID, application_id: UUID, **kwargs) -> ResumeVersion:
        version = ResumeVersion(tenant_id=tenant_id, application_id=application_id, **kwargs)
        return await self.add(version)


class ResumeScoreRepository(BaseRepository[ResumeScore]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResumeScore)

    async def create(self, tenant_id: UUID, application_id: UUID, **kwargs) -> ResumeScore:
        score = ResumeScore(tenant_id=tenant_id, application_id=application_id, **kwargs)
        return await self.add(score)

    async def average_score(self, tenant_id: UUID) -> tuple[float | None, int]:
        q = select(func.avg(ResumeScore.overall_score), func.count(ResumeScore.id)).where(
            ResumeScore.tenant_id == tenant_id
        )
        row = (await self._session.execute(q)).one()
        avg, count = row[0], row[1]
        return (float(avg) if avg is not None else None, count)


class ScreeningInterviewRepository(BaseRepository[ScreeningInterview]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ScreeningInterview)

    async def get_by_application(self, application_id: UUID, tenant_id: UUID) -> ScreeningInterview | None:
        result = await self._session.execute(
            select(ScreeningInterview).where(
                ScreeningInterview.application_id == application_id,
                ScreeningInterview.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_for_application(self, tenant_id: UUID, application_id: UUID, **kwargs) -> ScreeningInterview:
        existing = await self.get_by_application(application_id, tenant_id)
        if existing:
            for k, v in kwargs.items():
                setattr(existing, k, v)
            await self._session.flush()
            return existing
        record = ScreeningInterview(tenant_id=tenant_id, application_id=application_id, **kwargs)
        return await self.add(record)

    async def average_interview_score(self, tenant_id: UUID) -> tuple[float | None, int]:
        from app.models.candidate import InterviewStatus

        q = select(func.avg(ScreeningInterview.technical_score), func.count(ScreeningInterview.id)).where(
            ScreeningInterview.tenant_id == tenant_id,
            ScreeningInterview.status == InterviewStatus.COMPLETED,
        )
        row = (await self._session.execute(q)).one()
        return (float(row[0]) if row[0] is not None else None, row[1])

    async def count_pending(self, tenant_id: UUID) -> int:
        from app.models.candidate import InterviewStatus

        q = select(func.count(ScreeningInterview.id)).where(
            ScreeningInterview.tenant_id == tenant_id,
            ScreeningInterview.status == InterviewStatus.SCHEDULED,
        )
        return (await self._session.execute(q)).scalar_one()

    async def get_todays_interviews(self, tenant_id: UUID, limit: int = 10) -> list[ScreeningInterview]:
        from datetime import date

        today = date.today()
        q = (
            select(ScreeningInterview)
            .where(ScreeningInterview.tenant_id == tenant_id)
            .options(selectinload(ScreeningInterview.application).selectinload(CandidateApplication.candidate))
            .options(
                selectinload(ScreeningInterview.application)
                .selectinload(CandidateApplication.job_requirement)
                .selectinload(JobRequirement.client)
            )
            .order_by(ScreeningInterview.scheduled_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(q)
        interviews = list(result.scalars().all())
        return [i for i in interviews if i.scheduled_at and i.scheduled_at.date() == today]


class ResumeTemplateRepository(BaseRepository[ResumeTemplate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResumeTemplate)

    async def list_available(self, tenant_id: UUID) -> list[ResumeTemplate]:
        result = await self._session.execute(
            select(ResumeTemplate)
            .where(
                ResumeTemplate.is_deleted.is_(False),
                or_(ResumeTemplate.tenant_id == tenant_id, ResumeTemplate.tenant_id.is_(None)),
            )
            .order_by(ResumeTemplate.is_default.desc(), ResumeTemplate.name.asc())
        )
        return list(result.scalars().all())

    async def count_system_templates(self) -> int:
        q = select(func.count(ResumeTemplate.id)).where(
            ResumeTemplate.tenant_id.is_(None),
            ResumeTemplate.is_deleted.is_(False),
        )
        return (await self._session.execute(q)).scalar_one()

    async def get_by_id_for_tenant(self, template_id: UUID, tenant_id: UUID) -> ResumeTemplate | None:
        result = await self._session.execute(
            select(ResumeTemplate).where(
                ResumeTemplate.id == template_id,
                ResumeTemplate.is_deleted.is_(False),
                or_(ResumeTemplate.tenant_id == tenant_id, ResumeTemplate.tenant_id.is_(None)),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, tenant_id: UUID, **kwargs) -> ResumeTemplate:
        template = ResumeTemplate(tenant_id=tenant_id, **kwargs)
        return await self.add(template)

    async def clear_default_for_tenant(self, tenant_id: UUID) -> None:
        result = await self._session.execute(
            select(ResumeTemplate).where(
                ResumeTemplate.tenant_id == tenant_id,
                ResumeTemplate.is_default.is_(True),
                ResumeTemplate.is_deleted.is_(False),
            )
        )
        for template in result.scalars().all():
            template.is_default = False
