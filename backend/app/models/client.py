"""Client management models for recruitment consultancy."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import AuditMixin, TimestampMixin, UUIDPrimaryKeyMixin


class ClientStatus(str, enum.Enum):
    """Client company lifecycle status."""

    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"


class ContactType(str, enum.Enum):
    """Contact role within a client organization."""

    GENERAL = "general"
    HIRING_MANAGER = "hiring_manager"
    PRIMARY = "primary"


class Client(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Client company managed by the recruitment consultancy."""

    __tablename__ = "clients"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ClientStatus] = mapped_column(
        Enum(ClientStatus, name="client_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ClientStatus.PROSPECT,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    contacts: Mapped[list["ClientContact"]] = relationship(
        "ClientContact",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    locations: Mapped[list["ClientLocation"]] = relationship(
        "ClientLocation",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["ClientNote"]] = relationship(
        "ClientNote",
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="ClientNote.created_at.desc()",
    )
    job_requirements: Mapped[list["JobRequirement"]] = relationship(
        "JobRequirement",
        back_populates="client",
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name}>"


class ClientContact(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Contact person at a client company."""

    __tablename__ = "client_contacts"
    __table_args__ = (
        UniqueConstraint("client_id", "email", name="uq_client_contacts_client_email"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    contact_type: Mapped[ContactType] = mapped_column(
        Enum(ContactType, name="contact_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ContactType.GENERAL,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    client: Mapped["Client"] = relationship("Client", back_populates="contacts")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<ClientContact id={self.id} name={self.full_name}>"


class ClientLocation(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Physical office location for a client company."""

    __tablename__ = "client_locations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_headquarters: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    client: Mapped["Client"] = relationship("Client", back_populates="locations")

    def __repr__(self) -> str:
        return f"<ClientLocation id={self.id} name={self.name}>"


class ClientNote(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Note attached to a client record."""

    __tablename__ = "client_notes"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    client: Mapped["Client"] = relationship("Client", back_populates="notes")

    def __repr__(self) -> str:
        return f"<ClientNote id={self.id} client_id={self.client_id}>"
