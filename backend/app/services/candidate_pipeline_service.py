"""Candidate pipeline orchestration — resume parse, build, score, interview."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.candidate import (
    ApplicationStatus,
    InterviewStatus,
    ParseStatus,
    PipelineStage,
    RecruiterReviewDecision,
    ResumeVersionStatus,
)
from app.providers.base import AIProvider
from app.repositories.candidate_repository import (
    CandidateApplicationRepository,
    CandidateDocumentRepository,
    CandidateRepository,
    ParsedResumeRepository,
    ResumeScoreRepository,
    ResumeVersionRepository,
    ScreeningInterviewRepository,
)
from app.repositories.job_requirement_repository import JobRequirementRepository
from app.schemas.candidate import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationSummaryResponse,
    BuildResumeRequest,
    CandidateCreate,
    CandidateListResponse,
    CandidateResponse,
    CandidateUpdate,
    InterviewQuestionResponse,
    ParsedResumeResponse,
    RecruiterReviewRequest,
    ResumeBuildContextResponse,
    ResumeScoreResponse,
    ResumeVersionResponse,
    ScheduleInterviewRequest,
    ScreeningInterviewResponse,
    UpdateResumeVersionRequest,
)
from app.services.audit_service import AuditService
from app.services.resume_timeline_analysis import analyze_resume_for_job
from app.services.interview_flow import (
    TOTAL_INTERVIEW_QUESTIONS,
    build_question_response_payload,
    question_type_for_index,
)
from app.services.resume_export_service import ResumeExportService
from app.services.resume_template_service import ResumeTemplateService
from app.services.storage_service import StorageService
from app.services.tenant_settings_service import TenantSettingsService
from app.utils.document_extractor import extract_text_from_document

logger = get_logger(__name__)


class CandidatePipelineService:
    """End-to-end candidate recruitment pipeline."""

    def __init__(
        self,
        candidate_repo: CandidateRepository,
        application_repo: CandidateApplicationRepository,
        document_repo: CandidateDocumentRepository,
        parsed_repo: ParsedResumeRepository,
        version_repo: ResumeVersionRepository,
        score_repo: ResumeScoreRepository,
        interview_repo: ScreeningInterviewRepository,
        job_repo: JobRequirementRepository,
        audit_service: AuditService,
        storage_service: StorageService,
        export_service: ResumeExportService,
        settings_service: TenantSettingsService,
        template_service: ResumeTemplateService,
    ) -> None:
        self._candidate_repo = candidate_repo
        self._application_repo = application_repo
        self._document_repo = document_repo
        self._parsed_repo = parsed_repo
        self._version_repo = version_repo
        self._score_repo = score_repo
        self._interview_repo = interview_repo
        self._job_repo = job_repo
        self._audit = audit_service
        self._storage = storage_service
        self._export = export_service
        self._settings = settings_service
        self._templates = template_service

    async def _ai(self, tenant_id: UUID) -> AIProvider:
        return await self._settings.get_ai_provider(tenant_id)

    def _candidate_response(self, c) -> CandidateResponse:
        return CandidateResponse(
            id=c.id, first_name=c.first_name, last_name=c.last_name, full_name=c.full_name,
            email=c.email, phone=c.phone, linkedin_url=c.linkedin_url, github_url=c.github_url,
            portfolio_url=c.portfolio_url, current_company=c.current_company,
            current_ctc=c.current_ctc, expected_ctc=c.expected_ctc, notice_period_days=c.notice_period_days,
            notes=c.notes, created_at=c.created_at, updated_at=c.updated_at,
        )

    async def _get_application(self, app_id: UUID, tenant_id: UUID) -> object:
        app = await self._application_repo.get_by_id_for_tenant(app_id, tenant_id, full=True)
        if app is None:
            raise NotFoundError("Application not found")
        return app

    def _build_application_summary(self, app) -> ApplicationSummaryResponse:
        job = app.job_requirement
        ps = app.pipeline_stage
        st = app.status

        parsed = app.parsed_resume
        parse_status = parsed.status.value if parsed and hasattr(parsed.status, "value") else (parsed.status if parsed else None)
        has_parsed_resume = parse_status == ParseStatus.COMPLETED.value

        versions = [v for v in app.resume_versions if not v.is_deleted]
        latest_version = versions[-1] if versions else None

        scores = sorted(app.resume_scores, key=lambda s: s.created_at)
        latest_score: Decimal | None = None
        if latest_version:
            built_scores = [s for s in scores if s.resume_version_id == latest_version.id]
            if built_scores:
                latest_score = built_scores[-1].overall_score
        if latest_score is None:
            parsed_scores = [s for s in scores if s.resume_version_id is None]
            if parsed_scores:
                latest_score = parsed_scores[-1].overall_score

        interview = app.screening_interview
        interview_status = None
        interview_overall_score: Decimal | None = None
        if interview:
            interview_status = interview.status.value if hasattr(interview.status, "value") else interview.status
            score_fields = [
                interview.technical_score,
                interview.coding_score,
                interview.communication_score,
                interview.confidence_score,
                interview.problem_solving_score,
            ]
            numeric_scores = [float(f) for f in score_fields if f is not None]
            if numeric_scores:
                interview_overall_score = Decimal(str(round(sum(numeric_scores) / len(numeric_scores), 2)))

        latest_version_status = None
        if latest_version:
            latest_version_status = (
                latest_version.status.value if hasattr(latest_version.status, "value") else latest_version.status
            )

        return ApplicationSummaryResponse(
            id=app.id,
            candidate_id=app.candidate_id,
            candidate_name=app.candidate.full_name,
            job_requirement_id=app.job_requirement_id,
            job_title=job.title if job else "",
            client_name=job.client.name if job and job.client else "",
            pipeline_stage=ps.value if hasattr(ps, "value") else ps,
            status=st.value if hasattr(st, "value") else st,
            has_parsed_resume=has_parsed_resume,
            resume_version_count=len(versions),
            latest_resume_version_id=latest_version.id if latest_version else None,
            latest_built_resume_status=latest_version_status,
            latest_score=latest_score,
            interview_status=interview_status,
            interview_overall_score=interview_overall_score,
            created_at=app.created_at,
            updated_at=app.updated_at,
        )

    def _build_application_detail(self, app) -> ApplicationDetailResponse:
        job = app.job_requirement
        parsed = None
        if app.parsed_resume:
            parsed = ParsedResumeResponse.model_validate(app.parsed_resume)
        interview = None
        if app.screening_interview:
            interview = ScreeningInterviewResponse.model_validate(app.screening_interview)
        latest_score = app.resume_scores[-1].overall_score if app.resume_scores else None
        return ApplicationDetailResponse(
            id=app.id, tenant_id=app.tenant_id, candidate_id=app.candidate_id,
            candidate=self._candidate_response(app.candidate),
            job_requirement_id=app.job_requirement_id,
            job_title=job.title if job else "",
            client_name=job.client.name if job and job.client else "",
            job_description=job.description if job else None,
            job_experience_min_years=job.experience_min_years if job else None,
            job_experience_max_years=job.experience_max_years if job else None,
            pipeline_stage=app.pipeline_stage.value if hasattr(app.pipeline_stage, "value") else app.pipeline_stage,
            status=app.status.value if hasattr(app.status, "value") else app.status,
            recruiter_notes=app.recruiter_notes,
            parsed_resume=parsed,
            resume_versions=[ResumeVersionResponse.model_validate(v) for v in app.resume_versions if not v.is_deleted],
            resume_scores=[ResumeScoreResponse.model_validate(s) for s in app.resume_scores],
            screening_interview=interview,
            created_at=app.created_at, updated_at=app.updated_at,
        )

    async def create_candidate(self, tenant_id: UUID, data: CandidateCreate, user_id: UUID) -> CandidateResponse:
        candidate = await self._candidate_repo.create(
            tenant_id,
            first_name=data.first_name, last_name=data.last_name,
            email=str(data.email) if data.email else None,
            phone=data.phone, linkedin_url=data.linkedin_url, github_url=data.github_url,
            portfolio_url=data.portfolio_url, current_company=data.current_company,
            current_ctc=data.current_ctc, expected_ctc=data.expected_ctc,
            notice_period_days=data.notice_period_days, notes=data.notes,
            created_by=user_id, updated_by=user_id,
        )
        if data.job_requirement_id:
            job = await self._job_repo.get_by_id_for_tenant(data.job_requirement_id, tenant_id)
            if job is None:
                raise NotFoundError("Job requirement not found")
            await self._application_repo.create(
                tenant_id, candidate.id, data.job_requirement_id,
                created_by=user_id, updated_by=user_id,
            )
        await self._audit.log(tenant_id, "candidate.created", "candidate", user_id=user_id, resource_id=str(candidate.id))
        return self._candidate_response(candidate)

    async def create_application(
        self, tenant_id: UUID, candidate_id: UUID, job_requirement_id: UUID,
        recruiter_notes: str | None, user_id: UUID,
    ) -> ApplicationDetailResponse:
        candidate = await self._candidate_repo.get_by_id_for_tenant(candidate_id, tenant_id)
        if candidate is None:
            raise NotFoundError("Candidate not found")
        job = await self._job_repo.get_by_id_for_tenant(job_requirement_id, tenant_id)
        if job is None:
            raise NotFoundError("Job requirement not found")
        app = await self._application_repo.create(
            tenant_id, candidate_id, job_requirement_id,
            recruiter_notes=recruiter_notes, created_by=user_id, updated_by=user_id,
        )
        await self._audit.log(tenant_id, "application.created", "candidate_application", user_id=user_id, resource_id=str(app.id))
        return await self.get_application(app.id, tenant_id)

    async def list_candidates(self, tenant_id: UUID, search: str | None, page: int, page_size: int) -> CandidateListResponse:
        items, total = await self._candidate_repo.list_for_tenant(tenant_id, search=search, page=page, page_size=page_size)
        return CandidateListResponse(
            items=[self._candidate_response(c) for c in items], total=total, page=page, page_size=page_size,
            total_pages=self._candidate_repo.total_pages(total, page_size),
        )

    async def get_candidate(self, candidate_id: UUID, tenant_id: UUID) -> CandidateResponse:
        c = await self._candidate_repo.get_by_id_for_tenant(candidate_id, tenant_id)
        if c is None:
            raise NotFoundError("Candidate not found")
        return self._candidate_response(c)

    async def update_candidate(self, candidate_id: UUID, tenant_id: UUID, data: CandidateUpdate, user_id: UUID) -> CandidateResponse:
        c = await self._candidate_repo.get_by_id_for_tenant(candidate_id, tenant_id)
        if c is None:
            raise NotFoundError("Candidate not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "email" and value is not None:
                value = str(value)
            setattr(c, field, value)
        c.updated_by = user_id
        await self._candidate_repo._session.flush()
        return self._candidate_response(c)

    async def list_applications(
        self, tenant_id: UUID, candidate_id: UUID | None, job_id: UUID | None,
        pipeline_stage: str | None, page: int, page_size: int,
    ) -> ApplicationListResponse:
        items, total = await self._application_repo.list_for_tenant(
            tenant_id, candidate_id=candidate_id, job_requirement_id=job_id,
            pipeline_stage=pipeline_stage, page=page, page_size=page_size,
        )
        summaries = [self._build_application_summary(app) for app in items]
        return ApplicationListResponse(
            items=summaries, total=total, page=page, page_size=page_size,
            total_pages=self._candidate_repo.total_pages(total, page_size),
        )

    async def get_application(self, app_id: UUID, tenant_id: UUID) -> ApplicationDetailResponse:
        app = await self._get_application(app_id, tenant_id)
        return self._build_application_detail(app)

    async def upload_resume(
        self, app_id: UUID, tenant_id: UUID, file_name: str, content: bytes,
        content_type: str | None, user_id: UUID,
    ) -> ParsedResumeResponse:
        app = await self._get_application(app_id, tenant_id)
        object_key, size = self._storage.upload_candidate_resume(tenant_id, app_id, file_name, content, content_type)
        doc = await self._document_repo.create(
            tenant_id, app_id, document_type="resume", file_name=file_name,
            file_key=object_key, content_type=content_type, file_size_bytes=size,
            is_original_resume=True, created_by=user_id, updated_by=user_id,
        )
        parsed = await self._parsed_repo.upsert_for_application(
            tenant_id, app_id, document_id=doc.id, status=ParseStatus.PROCESSING,
        )
        try:
            text = extract_text_from_document(content, content_type, file_name)
            structured = await (await self._ai(tenant_id)).parse_resume(text)
            parsed.status = ParseStatus.COMPLETED
            parsed.structured_data = structured
            parsed.parsed_at = datetime.now(timezone.utc)
            parsed.error_message = None
            app.pipeline_stage = PipelineStage.SCREENING
            await self._application_repo._session.flush()
            await self._audit.log(tenant_id, "candidate.resume.parsed", "parsed_resume", user_id=user_id, resource_id=str(parsed.id))
            try:
                await self.score_resume(app_id, tenant_id, user_id, version_id=None)
            except Exception as score_exc:
                logger.warning("auto_score_parsed_resume_failed", error=str(score_exc))
        except Exception as exc:
            parsed.status = ParseStatus.FAILED
            parsed.error_message = str(exc)
            await self._parsed_repo._session.flush()
            logger.error("resume_parse_failed", application_id=str(app_id), error=str(exc))
            raise ValidationError(f"Resume parsing failed: {exc}") from exc
        return ParsedResumeResponse.model_validate(parsed)

    def _merge_build_inputs(self, base: dict, data: BuildResumeRequest) -> dict:
        merged = dict(base)
        if data.summary is not None:
            merged["summary"] = data.summary
        if data.skills is not None:
            merged["skills"] = data.skills
        if data.experience is not None:
            merged["experience"] = data.experience
        if data.education is not None:
            merged["education"] = data.education
        if data.training_entry and data.gap_strategy == "add_training_entry":
            experience = list(merged.get("experience") or [])
            entry = dict(data.training_entry)
            entry.setdefault("bullets", [])
            experience.append(entry)
            merged["experience"] = experience
        return merged

    async def get_resume_build_context(self, app_id: UUID, tenant_id: UUID) -> ResumeBuildContextResponse:
        app = await self._get_application(app_id, tenant_id)
        if not app.parsed_resume or app.parsed_resume.status != ParseStatus.COMPLETED:
            raise ValidationError("Resume must be parsed before preparing build inputs")
        job = app.job_requirement
        if not job:
            raise NotFoundError("Job requirement not found")
        parsed = app.parsed_resume.structured_data or {}
        analysis = analyze_resume_for_job(
            parsed,
            job.experience_min_years,
            job.experience_max_years,
        )
        template_list = await self._templates.list_templates(tenant_id)
        default_template_id = None
        for tpl in template_list.items:
            if tpl.is_default:
                default_template_id = tpl.id
                break
        if default_template_id is None and template_list.items:
            default_template_id = template_list.items[0].id
        return ResumeBuildContextResponse(
            job_experience_min_years=analysis["job_experience_min_years"],
            job_experience_max_years=analysis["job_experience_max_years"],
            candidate_total_experience_years=analysis["candidate_total_experience_years"],
            experience_shortfall_years=analysis["experience_shortfall_years"],
            timeline_gaps=analysis["timeline_gaps"],
            gap_strategy_options=analysis["gap_strategy_options"],
            recommendations=analysis["recommendations"],
            default_summary=parsed.get("summary"),
            default_skills=list(parsed.get("skills") or []),
            default_experience=list(parsed.get("experience") or []),
            default_education=list(parsed.get("education") or []),
            templates=template_list.items,
            default_template_id=default_template_id,
        )

    async def build_resume(self, app_id: UUID, tenant_id: UUID, data: BuildResumeRequest, user_id: UUID) -> ResumeVersionResponse:
        app = await self._get_application(app_id, tenant_id)
        if not app.parsed_resume or app.parsed_resume.status != ParseStatus.COMPLETED:
            raise ValidationError("Resume must be parsed before building")
        job = app.job_requirement
        if not job:
            raise NotFoundError("Job requirement not found")
        candidate_profile = {
            "first_name": app.candidate.first_name, "last_name": app.candidate.last_name,
            "email": app.candidate.email, "phone": app.candidate.phone,
            "current_company": app.candidate.current_company,
        }
        base_parsed = app.parsed_resume.structured_data or {}
        merged_parsed = self._merge_build_inputs(base_parsed, data)
        if not data.template_id:
            raise ValidationError("Select a resume template before building")
        resolved_template = await self._templates.resolve_template(data.template_id, tenant_id)
        if resolved_template is None:
            raise ValidationError("Selected resume template not found")

        analysis = analyze_resume_for_job(
            merged_parsed,
            job.experience_min_years,
            job.experience_max_years,
        )
        build_context = {
            "gap_strategy": data.gap_strategy,
            "target_total_experience_years": data.target_total_experience_years,
            "timeline_analysis": analysis,
            "training_entry": data.training_entry if data.gap_strategy == "add_training_entry" else None,
            "resume_template": {
                "id": str(resolved_template.id),
                "name": resolved_template.name,
                "description": resolved_template.description or "",
                "source_type": (resolved_template.config or {}).get("source_type", "html"),
            },
        }
        layout = resolved_template.html_template
        if layout and len(layout) <= 6000:
            build_context["resume_template"]["html_layout"] = layout

        content = await (await self._ai(tenant_id)).build_resume(
            candidate_profile,
            merged_parsed,
            job.description or job.title,
            data.recruiter_notes or app.recruiter_notes,
            build_context=build_context,
        )
        version_num = await self._version_repo.next_version_number(app_id)
        version = await self._version_repo.create(
            tenant_id, app_id, version_number=version_num,
            status=ResumeVersionStatus.PENDING_REVIEW, content_json=content,
            template_id=resolved_template.id,
            created_by=user_id, updated_by=user_id,
        )
        await self._audit.log(tenant_id, "candidate.resume.built", "resume_version", user_id=user_id, resource_id=str(version.id))
        try:
            await self.score_resume(app_id, tenant_id, user_id, version_id=version.id)
        except Exception as score_exc:
            logger.warning("auto_score_built_resume_failed", error=str(score_exc))
        version_resp = ResumeVersionResponse.model_validate(version)
        return version_resp.model_copy(update={"template_name": resolved_template.name})

    async def update_resume_version(
        self, app_id: UUID, version_id: UUID, tenant_id: UUID, data: UpdateResumeVersionRequest, user_id: UUID,
    ) -> ResumeVersionResponse:
        version = await self._version_repo.get_by_id_for_application(version_id, app_id, tenant_id)
        if version is None:
            raise NotFoundError("Resume version not found")
        version.content_json = data.content_json
        version.updated_by = user_id
        await self._version_repo._session.flush()
        return ResumeVersionResponse.model_validate(version)

    async def review_resume(
        self, app_id: UUID, version_id: UUID, tenant_id: UUID, data: RecruiterReviewRequest, user_id: UUID,
    ) -> ResumeVersionResponse:
        version = await self._version_repo.get_by_id_for_application(version_id, app_id, tenant_id)
        if version is None:
            raise NotFoundError("Resume version not found")
        version.recruiter_review_decision = data.decision
        version.recruiter_review_notes = data.notes
        version.reviewed_by = user_id
        version.reviewed_at = datetime.now(timezone.utc)
        if data.decision == RecruiterReviewDecision.ACCEPT or data.decision == RecruiterReviewDecision.SUBMIT_TO_CLIENT:
            version.status = ResumeVersionStatus.APPROVED
        elif data.decision == RecruiterReviewDecision.REJECT:
            version.status = ResumeVersionStatus.REJECTED
        elif data.decision == RecruiterReviewDecision.NEEDS_RESUME_CHANGES:
            version.status = ResumeVersionStatus.NEEDS_CHANGES
        version.updated_by = user_id
        app = await self._get_application(app_id, tenant_id)
        if data.decision == RecruiterReviewDecision.SUBMIT_TO_CLIENT:
            app.pipeline_stage = PipelineStage.SUBMITTED
        await self._application_repo._session.flush()
        return ResumeVersionResponse.model_validate(version)

    async def score_resume(self, app_id: UUID, tenant_id: UUID, user_id: UUID, version_id: UUID | None = None) -> ResumeScoreResponse:
        app = await self._get_application(app_id, tenant_id)
        job = app.job_requirement
        if not job:
            raise NotFoundError("Job requirement not found")
        resume_json = None
        if version_id:
            v = await self._version_repo.get_by_id_for_application(version_id, app_id, tenant_id)
            if v:
                resume_json = v.content_json
        elif app.resume_versions:
            resume_json = app.resume_versions[-1].content_json
        elif app.parsed_resume and app.parsed_resume.structured_data:
            resume_json = app.parsed_resume.structured_data
        if not resume_json:
            raise ValidationError("No resume data available to score")
        result = await (await self._ai(tenant_id)).score_resume(
            resume_json, job.description or "", job.required_skills or [], job.preferred_skills or [],
        )
        score = await self._score_repo.create(
            tenant_id, app_id, resume_version_id=version_id,
            overall_score=Decimal(str(result.get("overall_score", 0))),
            keyword_match=Decimal(str(result.get("keyword_match", 0))),
            skill_match=Decimal(str(result.get("skill_match", 0))),
            experience_match=Decimal(str(result.get("experience_match", 0))),
            semantic_similarity=Decimal(str(result.get("semantic_similarity", 0))),
            formatting_score=Decimal(str(result.get("formatting", 0))),
            grammar_score=Decimal(str(result.get("grammar", 0))),
            achievements_score=Decimal(str(result.get("achievements", 0))),
            missing_keywords=result.get("missing_keywords", []),
            suggestions=result.get("suggestions", []),
            improvement_areas=result.get("improvement_areas", []),
        )
        await self._audit.log(tenant_id, "candidate.resume.scored", "resume_score", user_id=user_id, resource_id=str(score.id))
        return ResumeScoreResponse.model_validate(score)

    async def export_resume(self, app_id: UUID, tenant_id: UUID, format: str, version_id: UUID | None) -> tuple[bytes, str, str]:
        app = await self._get_application(app_id, tenant_id)
        content_json = None
        version_record = None
        if version_id:
            version_record = await self._version_repo.get_by_id_for_application(version_id, app_id, tenant_id)
            content_json = version_record.content_json if version_record else None
        elif app.resume_versions:
            version_record = app.resume_versions[-1]
            content_json = version_record.content_json
        if not content_json:
            raise ValidationError("No resume version to export")

        html_template: str | None = None
        css_styles: str | None = None
        if version_record and version_record.template_id:
            template = await self._templates.resolve_template(version_record.template_id, tenant_id)
            if template:
                html_template = template.html_template
                css_styles = template.css_styles

        name = app.candidate.full_name.replace(" ", "_")
        if format == "docx":
            return self._export.export_docx(content_json), f"{name}_resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if format == "pdf":
            return self._export.export_pdf(content_json, html_template=html_template, css_styles=css_styles), f"{name}_resume.pdf", "application/pdf"
        if format == "html":
            return self._export.export_html(content_json, html_template=html_template, css_styles=css_styles), f"{name}_resume.html", "text/html"
        if format == "json":
            return self._export.export_json_bytes(content_json), f"{name}_resume.json", "application/json"
        raise ValidationError("Format must be pdf, docx, html, or json")

    async def schedule_interview(self, app_id: UUID, tenant_id: UUID, data: ScheduleInterviewRequest, user_id: UUID) -> ScreeningInterviewResponse:
        app = await self._get_application(app_id, tenant_id)
        link_id = uuid4()
        interview = await self._interview_repo.upsert_for_application(
            tenant_id, app_id,
            status=InterviewStatus.SCHEDULED,
            scheduled_at=data.scheduled_at, duration_minutes=data.duration_minutes,
            difficulty=data.difficulty, coding_required=data.coding_required,
            behavioral=data.behavioral, technical=data.technical,
            language=data.language, timezone=data.timezone,
            interview_link=f"/interview/{link_id}",
            created_by=user_id, updated_by=user_id,
        )
        app.pipeline_stage = PipelineStage.INTERVIEW
        await self._application_repo._session.flush()
        await self._audit.log(tenant_id, "candidate.interview.scheduled", "screening_interview", user_id=user_id, resource_id=str(interview.id))
        return ScreeningInterviewResponse.model_validate(interview)

    def _resume_json_for_app(self, app) -> dict:
        if app.resume_versions:
            return app.resume_versions[-1].content_json
        if app.parsed_resume and app.parsed_resume.structured_data:
            return app.parsed_resume.structured_data
        return {}

    async def _generate_question_at_index(
        self, tenant_id: UUID, app, question_index: int,
    ) -> dict:
        job = app.job_requirement
        resume_json = self._resume_json_for_app(app)
        interview = app.screening_interview
        transcript = list(interview.transcript or []) if interview else []
        questions = [t["content"] for t in transcript if t.get("role") == "ai"]
        answers = [t["content"] for t in transcript if t.get("role") == "candidate"]
        q_type = question_type_for_index(question_index)
        return await (await self._ai(tenant_id)).generate_interview_question(
            resume_json,
            job.description or "" if job else "",
            questions,
            answers,
            question_type=q_type,
            question_number=question_index + 1,
        )

    async def start_interview(self, app_id: UUID, tenant_id: UUID) -> InterviewQuestionResponse:
        app = await self._get_application(app_id, tenant_id)
        interview = app.screening_interview
        if not interview:
            raise ValidationError("Interview not scheduled")
        interview.status = InterviewStatus.IN_PROGRESS
        interview.transcript = []
        question_data = await self._generate_question_at_index(tenant_id, app, 0)
        q_type = question_type_for_index(0)
        interview.transcript.append({
            "role": "ai",
            "content": question_data.get("question", ""),
            "question_type": q_type,
            "options": question_data.get("options", []),
            "question_number": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await self._interview_repo._session.flush()
        payload = build_question_response_payload(question_data, 1, InterviewStatus.IN_PROGRESS)
        return InterviewQuestionResponse(**payload)

    async def submit_interview_answer(self, app_id: UUID, tenant_id: UUID, answer: str) -> InterviewQuestionResponse:
        app = await self._get_application(app_id, tenant_id)
        interview = app.screening_interview
        if not interview or interview.status != InterviewStatus.IN_PROGRESS:
            raise ValidationError("Interview not in progress")
        transcript = list(interview.transcript or [])
        transcript.append({
            "role": "candidate",
            "content": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        answers = [t["content"] for t in transcript if t.get("role") == "candidate"]
        if len(answers) >= TOTAL_INTERVIEW_QUESTIONS:
            interview.transcript = transcript
            await self._interview_repo._session.flush()
            return InterviewQuestionResponse(
                question="",
                interview_status=InterviewStatus.IN_PROGRESS,
                question_number=len(answers),
                question_type=question_type_for_index(len(answers) - 1),
                options=[],
                total_questions=TOTAL_INTERVIEW_QUESTIONS,
                is_complete=True,
            )
        next_index = len(answers)
        question_data = await self._generate_question_at_index(tenant_id, app, next_index)
        q_type = question_type_for_index(next_index)
        transcript.append({
            "role": "ai",
            "content": question_data.get("question", ""),
            "question_type": q_type,
            "options": question_data.get("options", []),
            "question_number": next_index + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        interview.transcript = transcript
        await self._interview_repo._session.flush()
        payload = build_question_response_payload(question_data, next_index + 1, InterviewStatus.IN_PROGRESS)
        return InterviewQuestionResponse(**payload)

    async def complete_interview(self, app_id: UUID, tenant_id: UUID, user_id: UUID) -> ScreeningInterviewResponse:
        app = await self._get_application(app_id, tenant_id)
        interview = app.screening_interview
        if not interview:
            raise ValidationError("Interview not found")
        job = app.job_requirement
        resume_json = (app.resume_versions[-1].content_json if app.resume_versions
                       else app.parsed_resume.structured_data if app.parsed_resume else {})
        summary = await (await self._ai(tenant_id)).summarize_interview(interview.transcript or [], resume_json, job.description or "")
        interview.status = InterviewStatus.COMPLETED
        interview.summary = summary.get("summary", "")
        interview.technical_score = Decimal(str(summary.get("technical_score", 0)))
        interview.coding_score = Decimal(str(summary.get("coding_score", 0))) if summary.get("coding_score") else None
        interview.communication_score = Decimal(str(summary.get("communication_score", 0)))
        interview.confidence_score = Decimal(str(summary.get("confidence_score", 0)))
        interview.problem_solving_score = Decimal(str(summary.get("problem_solving_score", 0)))
        rec = summary.get("recommendation", "hold")
        from app.models.candidate import HireRecommendation
        interview.recommendation = HireRecommendation(rec)
        interview.evaluation_data = summary
        interview.completed_at = datetime.now(timezone.utc)
        await self._interview_repo._session.flush()
        await self._audit.log(tenant_id, "candidate.interview.completed", "screening_interview", user_id=user_id, resource_id=str(interview.id))
        return ScreeningInterviewResponse.model_validate(interview)
