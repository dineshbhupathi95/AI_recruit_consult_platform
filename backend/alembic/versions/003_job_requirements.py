"""Job requirements and attachments tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_job_requirements"
down_revision: Union[str, None] = "002_client_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

employment_type_enum = postgresql.ENUM(
    "full_time", "part_time", "contract", "temporary", "internship",
    name="employment_type",
    create_type=False,
)
job_priority_enum = postgresql.ENUM(
    "low", "medium", "high", "urgent",
    name="job_priority",
    create_type=False,
)
job_status_enum = postgresql.ENUM(
    "draft", "open", "on_hold", "filled", "closed", "cancelled",
    name="job_status",
    create_type=False,
)


def upgrade() -> None:
    employment_type_enum.create(op.get_bind(), checkfirst=True)
    job_priority_enum.create(op.get_bind(), checkfirst=True)
    job_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "job_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hiring_manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("experience_min_years", sa.Integer(), nullable=True),
        sa.Column("experience_max_years", sa.Integer(), nullable=True),
        sa.Column("budget_min", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("budget_max", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("budget_currency", sa.String(length=3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("notice_period_days", sa.Integer(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column(
            "employment_type",
            employment_type_enum,
            nullable=False,
            server_default=sa.text("'full_time'"),
        ),
        sa.Column(
            "priority",
            job_priority_enum,
            nullable=False,
            server_default=sa.text("'medium'"),
        ),
        sa.Column(
            "status",
            job_status_enum,
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("preferred_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_location_id"], ["client_locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["hiring_manager_id"], ["client_contacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_requirements_tenant_id", "job_requirements", ["tenant_id"])
    op.create_index("ix_job_requirements_client_id", "job_requirements", ["client_id"])
    op.create_index("ix_job_requirements_title", "job_requirements", ["title"])
    op.create_index("ix_job_requirements_status", "job_requirements", ["status"])
    op.create_index("ix_job_requirements_priority", "job_requirements", ["priority"])
    op.create_index("ix_job_requirements_employment_type", "job_requirements", ["employment_type"])
    op.create_index("ix_job_requirements_is_deleted", "job_requirements", ["is_deleted"])
    op.create_index("ix_job_requirements_tenant_status", "job_requirements", ["tenant_id", "status"])

    op.create_table(
        "job_requirement_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_requirement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("file_key", sa.String(length=1024), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["job_requirement_id"], ["job_requirements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_requirement_id", "file_key", name="uq_job_attachments_job_file_key"),
    )
    op.create_index("ix_job_requirement_attachments_tenant_id", "job_requirement_attachments", ["tenant_id"])
    op.create_index("ix_job_requirement_attachments_job_id", "job_requirement_attachments", ["job_requirement_id"])


def downgrade() -> None:
    op.drop_table("job_requirement_attachments")
    op.drop_table("job_requirements")
    job_status_enum.drop(op.get_bind(), checkfirst=True)
    job_priority_enum.drop(op.get_bind(), checkfirst=True)
    employment_type_enum.drop(op.get_bind(), checkfirst=True)
