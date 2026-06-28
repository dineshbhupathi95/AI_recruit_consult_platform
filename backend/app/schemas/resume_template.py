"""Pydantic schemas for resume templates."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeTemplateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_default: bool
    is_system: bool
    source_type: str = "html"
    source_file_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ResumeTemplateDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID | None
    name: str
    description: str | None
    html_template: str
    css_styles: str
    config: dict[str, Any]
    is_default: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime


class ResumeTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    html_template: str = Field(min_length=1)
    css_styles: str = ""
    is_default: bool = False


class ResumeTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    html_template: str | None = None
    css_styles: str | None = None
    is_default: bool | None = None


class ResumeTemplateListResponse(BaseModel):
    items: list[ResumeTemplateSummary]
    total: int
