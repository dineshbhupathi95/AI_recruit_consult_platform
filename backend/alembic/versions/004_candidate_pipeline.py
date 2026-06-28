"""Candidate pipeline tables — candidates, applications, resumes, interviews."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_candidate_pipeline"
down_revision: Union[str, None] = "003_job_requirements"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pipeline_stage_enum = postgresql.ENUM(
    "sourced", "screening", "interview", "submitted", "placed",
    name="pipeline_stage",
    create_type=False,
)
application_status_enum = postgresql.ENUM(
    "active", "on_hold", "rejected", "withdrawn", "placed",
    name="application_status",
    create_type=False,
)
parse_status_enum = postgresql.ENUM(
    "pending", "processing", "completed", "failed",
    name="parse_status",
    create_type=False,
)
resume_version_status_enum = postgresql.ENUM(
    "draft", "pending_review", "approved", "needs_changes", "rejected",
    name="resume_version_status",
    create_type=False,
)
recruiter_review_decision_enum = postgresql.ENUM(
    "accept", "reject", "needs_more_interview", "needs_resume_changes", "submit_to_client",
    name="recruiter_review_decision",
    create_type=False,
)
interview_status_enum = postgresql.ENUM(
    "scheduled", "in_progress", "completed", "cancelled",
    name="interview_status",
    create_type=False,
)
hire_recommendation_enum = postgresql.ENUM(
    "strong_hire", "hire", "hold", "reject",
    name="hire_recommendation",
    create_type=False,
)


def upgrade() -> None:
    pipeline_stage_enum.create(op.get_bind(), checkfirst=True)
    application_status_enum.create(op.get_bind(), checkfirst=True)
    parse_status_enum.create(op.get_bind(), checkfirst=True)
    resume_version_status_enum.create(op.get_bind(), checkfirst=True)
    recruiter_review_decision_enum.create(op.get_bind(), checkfirst=True)
    interview_status_enum.create(op.get_bind(), checkfirst=True)
    hire_recommendation_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("linkedin_url", sa.String(length=512), nullable=True),
        sa.Column("github_url", sa.String(length=512), nullable=True),
        sa.Column("portfolio_url", sa.String(length=512), nullable=True),
        sa.Column("current_company", sa.String(length=255), nullable=True),
        sa.Column("current_ctc", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("expected_ctc", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("notice_period_days", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidates_tenant_id", "candidates", ["tenant_id"])
    op.create_index("ix_candidates_email", "candidates", ["email"])
    op.create_index("ix_candidates_is_deleted", "candidates", ["is_deleted"])

    op.create_table(
        "candidate_applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_requirement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "pipeline_stage",
            pipeline_stage_enum,
            nullable=False,
            server_default=sa.text("'sourced'"),
        ),
        sa.Column(
            "status",
            application_status_enum,
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("recruiter_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_requirement_id"], ["job_requirements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "job_requirement_id", name="uq_candidate_job"),
    )
    op.create_index("ix_candidate_applications_tenant_id", "candidate_applications", ["tenant_id"])
    op.create_index("ix_candidate_applications_candidate_id", "candidate_applications", ["candidate_id"])
    op.create_index("ix_candidate_applications_job_requirement_id", "candidate_applications", ["job_requirement_id"])
    op.create_index("ix_candidate_applications_pipeline_stage", "candidate_applications", ["pipeline_stage"])
    op.create_index("ix_candidate_applications_status", "candidate_applications", ["status"])

    op.create_table(
        "candidate_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False, server_default=sa.text("'resume'")),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("file_key", sa.String(length=1024), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("is_original_resume", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_documents_tenant_id", "candidate_documents", ["tenant_id"])
    op.create_index("ix_candidate_documents_application_id", "candidate_documents", ["application_id"])
    op.create_index("ix_candidate_documents_document_type", "candidate_documents", ["document_type"])

    op.create_table(
        "parsed_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            parse_status_enum,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("structured_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["candidate_documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id"),
    )
    op.create_index("ix_parsed_resumes_tenant_id", "parsed_resumes", ["tenant_id"])
    op.create_index("ix_parsed_resumes_status", "parsed_resumes", ["status"])

    op.create_table(
        "resume_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("html_template", sa.Text(), nullable=False),
        sa.Column("css_styles", sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_templates_tenant_id", "resume_templates", ["tenant_id"])

    op.create_table(
        "resume_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            resume_version_status_enum,
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column("content_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recruiter_review_decision", recruiter_review_decision_enum, nullable=True),
        sa.Column("recruiter_review_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["resume_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "version_number", name="uq_resume_version_app_number"),
    )
    op.create_index("ix_resume_versions_tenant_id", "resume_versions", ["tenant_id"])
    op.create_index("ix_resume_versions_application_id", "resume_versions", ["application_id"])
    op.create_index("ix_resume_versions_status", "resume_versions", ["status"])

    op.create_table(
        "resume_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("overall_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("keyword_match", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("skill_match", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("experience_match", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("semantic_similarity", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("formatting_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("grammar_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("achievements_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("missing_keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("suggestions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("improvement_areas", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_version_id"], ["resume_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_scores_tenant_id", "resume_scores", ["tenant_id"])
    op.create_index("ix_resume_scores_application_id", "resume_scores", ["application_id"])

    op.create_table(
        "screening_interviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            interview_status_enum,
            nullable=False,
            server_default=sa.text("'scheduled'"),
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default=sa.text("45")),
        sa.Column("difficulty", sa.String(length=50), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("coding_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("behavioral", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("technical", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("language", sa.String(length=50), nullable=False, server_default=sa.text("'en'")),
        sa.Column("timezone", sa.String(length=100), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("interview_link", sa.String(length=1024), nullable=True),
        sa.Column("transcript", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("technical_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("coding_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("communication_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("problem_solving_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("recommendation", hire_recommendation_enum, nullable=True),
        sa.Column("evaluation_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["candidate_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id"),
    )
    op.create_index("ix_screening_interviews_tenant_id", "screening_interviews", ["tenant_id"])
    op.create_index("ix_screening_interviews_status", "screening_interviews", ["status"])


def downgrade() -> None:
    op.drop_table("screening_interviews")
    op.drop_table("resume_scores")
    op.drop_table("resume_versions")
    op.drop_table("resume_templates")
    op.drop_table("parsed_resumes")
    op.drop_table("candidate_documents")
    op.drop_table("candidate_applications")
    op.drop_table("candidates")
    hire_recommendation_enum.drop(op.get_bind(), checkfirst=True)
    interview_status_enum.drop(op.get_bind(), checkfirst=True)
    recruiter_review_decision_enum.drop(op.get_bind(), checkfirst=True)
    resume_version_status_enum.drop(op.get_bind(), checkfirst=True)
    parse_status_enum.drop(op.get_bind(), checkfirst=True)
    application_status_enum.drop(op.get_bind(), checkfirst=True)
    pipeline_stage_enum.drop(op.get_bind(), checkfirst=True)
