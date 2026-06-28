"""Resume template API endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Form, Query, UploadFile, status
from fastapi.responses import HTMLResponse, Response

from app.core.dependencies import CurrentUser, ResumeTemplateServiceDep
from app.schemas.auth import MessageResponse
from app.schemas.resume_template import (
    ResumeTemplateCreate,
    ResumeTemplateDetail,
    ResumeTemplateListResponse,
    ResumeTemplateUpdate,
)

router = APIRouter(prefix="/resume-templates", tags=["Resume Templates"])


@router.get("", response_model=ResumeTemplateListResponse)
async def list_resume_templates(
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> ResumeTemplateListResponse:
    current_user.require_permission("candidates:read")
    return await service.list_templates(current_user.tenant_id)


@router.post("", response_model=ResumeTemplateDetail, status_code=status.HTTP_201_CREATED)
async def create_resume_template(
    data: ResumeTemplateCreate,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> ResumeTemplateDetail:
    current_user.require_permission("candidates:write")
    return await service.create_template(current_user.tenant_id, data, current_user.user_id)


@router.post("/upload", response_model=ResumeTemplateDetail, status_code=status.HTTP_201_CREATED)
async def upload_resume_template(
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    description: str | None = Form(default=None),
    is_default: bool = Form(default=False),
) -> ResumeTemplateDetail:
    current_user.require_permission("candidates:write")
    if not file.filename:
        from app.core.exceptions import ValidationError
        raise ValidationError("File name required")
    content = await file.read()
    return await service.create_template_from_upload(
        current_user.tenant_id,
        file.filename,
        content,
        file.content_type,
        current_user.user_id,
        name=name,
        description=description,
        is_default=is_default,
    )


@router.get("/{template_id}", response_model=ResumeTemplateDetail)
async def get_resume_template(
    template_id: UUID,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> ResumeTemplateDetail:
    current_user.require_permission("candidates:read")
    return await service.get_template(template_id, current_user.tenant_id)


@router.patch("/{template_id}", response_model=ResumeTemplateDetail)
async def update_resume_template(
    template_id: UUID,
    data: ResumeTemplateUpdate,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> ResumeTemplateDetail:
    current_user.require_permission("candidates:write")
    return await service.update_template(template_id, current_user.tenant_id, data, current_user.user_id)


@router.delete("/{template_id}", response_model=MessageResponse)
async def delete_resume_template(
    template_id: UUID,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> MessageResponse:
    current_user.require_permission("candidates:write")
    await service.delete_template(template_id, current_user.tenant_id, current_user.user_id)
    return MessageResponse(message="Template deleted")


@router.get("/{template_id}/preview", response_class=HTMLResponse)
async def preview_resume_template(
    template_id: UUID,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
    mode: str = Query(default="sample", pattern="^(sample|uploaded)$"),
) -> Response:
    current_user.require_permission("candidates:read")
    if mode == "uploaded":
        data, file_name, media_type = await service.get_source_file(template_id, current_user.tenant_id)
        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename={file_name}"},
        )
    html, _ = await service.preview_template(template_id, current_user.tenant_id)
    return HTMLResponse(content=html)


@router.get("/{template_id}/source")
async def download_resume_template_source(
    template_id: UUID,
    current_user: CurrentUser,
    service: ResumeTemplateServiceDep,
) -> Response:
    current_user.require_permission("candidates:read")
    data, file_name, media_type = await service.get_source_file(template_id, current_user.tenant_id)
    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename={file_name}"},
    )
