"""Resume template management."""

from uuid import UUID

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.data.resume_templates import SAMPLE_RESUME_JSON, SYSTEM_TEMPLATES
from app.models.candidate import ResumeTemplate
from app.providers.base import AIProvider
from app.repositories.candidate_repository import ResumeTemplateRepository
from app.schemas.resume_template import (
    ResumeTemplateCreate,
    ResumeTemplateDetail,
    ResumeTemplateListResponse,
    ResumeTemplateSummary,
    ResumeTemplateUpdate,
)
from app.services.resume_export_service import ResumeExportService
from app.services.storage_service import StorageService
from app.services.tenant_settings_service import TenantSettingsService
from app.utils.document_extractor import extract_text_from_document
from app.utils.resume_template_upload import docx_to_html, fallback_jinja_from_parsed

logger = get_logger(__name__)


class ResumeTemplateService:
    def __init__(
        self,
        template_repo: ResumeTemplateRepository,
        export_service: ResumeExportService,
        storage_service: StorageService,
        settings_service: TenantSettingsService,
    ) -> None:
        self._repo = template_repo
        self._export = export_service
        self._storage = storage_service
        self._settings = settings_service

    async def _ai(self, tenant_id: UUID) -> AIProvider:
        return await self._settings.get_ai_provider(tenant_id)

    async def _ensure_system_templates(self) -> None:
        if await self._repo.count_system_templates() > 0:
            return
        for spec in SYSTEM_TEMPLATES:
            template = ResumeTemplate(
                tenant_id=None,
                name=spec["name"],
                description=spec["description"],
                html_template=spec["html_template"],
                css_styles=spec["css_styles"],
                is_default=spec["is_default"],
                is_system=True,
            )
            await self._repo.add(template)

    def _summary_from_template(self, template: ResumeTemplate) -> ResumeTemplateSummary:
        cfg = template.config or {}
        base = ResumeTemplateSummary.model_validate(template)
        return base.model_copy(
            update={
                "source_type": cfg.get("source_type", "html"),
                "source_file_name": cfg.get("source_file_name"),
            }
        )

    def _to_detail(self, template: ResumeTemplate) -> ResumeTemplateDetail:
        return ResumeTemplateDetail.model_validate(template)

    async def list_templates(self, tenant_id: UUID) -> ResumeTemplateListResponse:
        await self._ensure_system_templates()
        items = await self._repo.list_available(tenant_id)
        summaries = [self._summary_from_template(t) for t in items]
        return ResumeTemplateListResponse(items=summaries, total=len(summaries))

    async def get_template(self, template_id: UUID, tenant_id: UUID) -> ResumeTemplateDetail:
        await self._ensure_system_templates()
        template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
        if template is None:
            raise NotFoundError("Resume template not found")
        return self._to_detail(template)

    async def create_template(
        self, tenant_id: UUID, data: ResumeTemplateCreate, user_id: UUID,
    ) -> ResumeTemplateDetail:
        if data.is_default:
            await self._repo.clear_default_for_tenant(tenant_id)
        template = await self._repo.create(
            tenant_id,
            name=data.name,
            description=data.description,
            html_template=data.html_template,
            css_styles=data.css_styles,
            config={"source_type": "html"},
            is_default=data.is_default,
            is_system=False,
            created_by=user_id,
            updated_by=user_id,
        )
        await self._repo._session.flush()
        return self._to_detail(template)

    async def create_template_from_upload(
        self,
        tenant_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        is_default: bool = False,
    ) -> ResumeTemplateDetail:
        lower_name = file_name.lower()
        is_pdf = content_type == "application/pdf" or lower_name.endswith(".pdf")
        is_docx = (
            content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or lower_name.endswith(".docx")
        )
        if not is_pdf and not is_docx:
            raise ValidationError("Upload a PDF or DOCX resume as the template")

        text = extract_text_from_document(content, content_type, file_name)
        parsed = await (await self._ai(tenant_id)).parse_resume(text)

        source_html: str | None = None
        if is_docx:
            try:
                source_html = docx_to_html(content)
            except Exception as exc:
                logger.warning("docx_to_html_failed", error=str(exc))

        try:
            converted = await (await self._ai(tenant_id)).convert_upload_to_jinja_template(
                source_html, parsed,
            )
            html_template = converted.get("html_template") or ""
            css_styles = converted.get("css_styles") or ""
            if not html_template.strip():
                raise ValueError("empty template")
        except Exception as exc:
            logger.warning("convert_upload_template_failed", error=str(exc))
            html_template, css_styles = fallback_jinja_from_parsed(parsed)

        display_name = (name or "").strip() or file_name.rsplit(".", 1)[0]
        if is_default:
            await self._repo.clear_default_for_tenant(tenant_id)

        template = await self._repo.create(
            tenant_id,
            name=display_name,
            description=description or "Uploaded resume used as layout template",
            html_template=html_template,
            css_styles=css_styles,
            config={"source_type": "upload"},
            is_default=is_default,
            is_system=False,
            created_by=user_id,
            updated_by=user_id,
        )
        await self._repo._session.flush()

        object_key, _ = self._storage.upload_resume_template(
            tenant_id, template.id, file_name, content, content_type,
        )
        template.config = {
            "source_type": "upload",
            "source_file_key": object_key,
            "source_file_name": file_name,
            "source_content_type": content_type,
        }
        await self._repo._session.flush()
        return self._to_detail(template)

    async def update_template(
        self, template_id: UUID, tenant_id: UUID, data: ResumeTemplateUpdate, user_id: UUID,
    ) -> ResumeTemplateDetail:
        template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
        if template is None:
            raise NotFoundError("Resume template not found")
        if template.is_system or template.tenant_id is None:
            raise ForbiddenError("System templates cannot be edited")
        if data.is_default:
            await self._repo.clear_default_for_tenant(tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)
        template.updated_by = user_id
        await self._repo._session.flush()
        return self._to_detail(template)

    async def delete_template(self, template_id: UUID, tenant_id: UUID, user_id: UUID) -> None:
        template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
        if template is None:
            raise NotFoundError("Resume template not found")
        if template.is_system or template.tenant_id is None:
            raise ForbiddenError("System templates cannot be deleted")
        cfg = template.config or {}
        file_key = cfg.get("source_file_key")
        if file_key:
            self._storage.delete_object(file_key)
        template.is_deleted = True
        template.updated_by = user_id
        await self._repo._session.flush()

    async def preview_template(
        self, template_id: UUID, tenant_id: UUID,
    ) -> tuple[str, str]:
        template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
        if template is None:
            raise NotFoundError("Resume template not found")
        html = self._export.render_html_from_template(
            SAMPLE_RESUME_JSON,
            template.html_template,
            template.css_styles,
        )
        return html, template.name

    async def get_source_file(
        self, template_id: UUID, tenant_id: UUID,
    ) -> tuple[bytes, str, str]:
        template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
        if template is None:
            raise NotFoundError("Resume template not found")
        cfg = template.config or {}
        file_key = cfg.get("source_file_key")
        if not file_key:
            raise ValidationError("This template has no uploaded source file")
        data, content_type = self._storage.get_object_bytes(file_key)
        file_name = cfg.get("source_file_name") or "template"
        media_type = content_type or cfg.get("source_content_type") or "application/octet-stream"
        return data, file_name, media_type

    async def resolve_template(
        self, template_id: UUID | None, tenant_id: UUID,
    ) -> ResumeTemplate | None:
        await self._ensure_system_templates()
        if template_id:
            template = await self._repo.get_by_id_for_tenant(template_id, tenant_id)
            if template is None:
                raise ValidationError("Selected resume template not found")
            return template
        items = await self._repo.list_available(tenant_id)
        default = next((t for t in items if t.is_default), None)
        return default or (items[0] if items else None)
