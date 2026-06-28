export type ClientStatus = "prospect" | "active" | "inactive" | "on_hold";
export type ContactType = "general" | "hiring_manager" | "primary";

export interface ClientContact {
  id: string;
  client_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string | null;
  job_title: string | null;
  department: string | null;
  contact_type: ContactType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientLocation {
  id: string;
  client_id: string;
  name: string;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  is_headquarters: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientNote {
  id: string;
  client_id: string;
  content: string;
  created_by: string | null;
  created_at: string;
}

export interface ClientSummary {
  id: string;
  name: string;
  industry: string | null;
  status: ClientStatus;
  email: string | null;
  phone: string | null;
  contact_count: number;
  location_count: number;
  hiring_manager_count: number;
  created_at: string;
  updated_at: string;
}

export interface ClientDetail {
  id: string;
  tenant_id: string;
  name: string;
  legal_name: string | null;
  industry: string | null;
  website: string | null;
  phone: string | null;
  email: string | null;
  status: ClientStatus;
  description: string | null;
  contacts: ClientContact[];
  locations: ClientLocation[];
  notes: ClientNote[];
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  items: ClientSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ClientCreatePayload {
  name: string;
  legal_name?: string;
  industry?: string;
  website?: string;
  phone?: string;
  email?: string;
  status?: ClientStatus;
  description?: string;
  contacts?: Omit<ClientContact, "id" | "client_id" | "full_name" | "created_at" | "updated_at">[];
  locations?: Omit<ClientLocation, "id" | "client_id" | "created_at" | "updated_at">[];
}

export interface ClientUpdatePayload {
  name?: string;
  legal_name?: string;
  industry?: string;
  website?: string;
  phone?: string;
  email?: string;
  status?: ClientStatus;
  description?: string;
}

export interface ContactCreatePayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  department?: string;
  contact_type?: ContactType;
  is_active?: boolean;
}

export interface LocationCreatePayload {
  name: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  is_headquarters?: boolean;
}

export interface NoteCreatePayload {
  content: string;
}

export const CLIENT_STATUS_LABELS: Record<ClientStatus, string> = {
  prospect: "Prospect",
  active: "Active",
  inactive: "Inactive",
  on_hold: "On Hold",
};

export const CONTACT_TYPE_LABELS: Record<ContactType, string> = {
  general: "General",
  hiring_manager: "Hiring Manager",
  primary: "Primary Contact",
};
