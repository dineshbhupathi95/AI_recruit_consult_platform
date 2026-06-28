"""Client management Pydantic schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientStatus(str, Enum):
    """Client company lifecycle status."""

    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"


class ContactType(str, Enum):
    """Contact role within a client organization."""

    GENERAL = "general"
    HIRING_MANAGER = "hiring_manager"
    PRIMARY = "primary"


class ClientContactCreate(BaseModel):
    """Create a client contact."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    contact_type: ContactType = ContactType.GENERAL
    is_active: bool = True


class ClientContactUpdate(BaseModel):
    """Update a client contact."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    contact_type: ContactType | None = None
    is_active: bool | None = None


class ClientContactResponse(BaseModel):
    """Client contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str | None
    job_title: str | None
    department: str | None
    contact_type: ContactType
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientLocationCreate(BaseModel):
    """Create a client location."""

    name: str = Field(..., min_length=1, max_length=255)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    is_headquarters: bool = False


class ClientLocationUpdate(BaseModel):
    """Update a client location."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    is_headquarters: bool | None = None


class ClientLocationResponse(BaseModel):
    """Client location response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    name: str
    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    is_headquarters: bool
    created_at: datetime
    updated_at: datetime


class ClientNoteCreate(BaseModel):
    """Create a client note."""

    content: str = Field(..., min_length=1, max_length=10000)


class ClientNoteResponse(BaseModel):
    """Client note response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    content: str
    created_by: UUID | None
    created_at: datetime


class ClientCreate(BaseModel):
    """Create a new client company."""

    name: str = Field(..., min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=512)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    status: ClientStatus = ClientStatus.PROSPECT
    description: str | None = Field(default=None, max_length=5000)
    contacts: list[ClientContactCreate] = Field(default_factory=list)
    locations: list[ClientLocationCreate] = Field(default_factory=list)


class ClientUpdate(BaseModel):
    """Update an existing client company."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=512)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    status: ClientStatus | None = None
    description: str | None = Field(default=None, max_length=5000)


class ClientSummaryResponse(BaseModel):
    """Client list item summary."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    industry: str | None
    status: ClientStatus
    email: str | None
    phone: str | None
    contact_count: int = 0
    location_count: int = 0
    hiring_manager_count: int = 0
    created_at: datetime
    updated_at: datetime


class ClientDetailResponse(BaseModel):
    """Full client detail with nested resources."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    legal_name: str | None
    industry: str | None
    website: str | None
    phone: str | None
    email: str | None
    status: ClientStatus
    description: str | None
    contacts: list[ClientContactResponse]
    locations: list[ClientLocationResponse]
    notes: list[ClientNoteResponse]
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseModel):
    """Paginated client list."""

    items: list[ClientSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ClientSearchParams(BaseModel):
    """Query parameters for client search."""

    search: str | None = Field(default=None, max_length=255)
    status: ClientStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
