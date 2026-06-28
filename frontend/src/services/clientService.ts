import { apiClient } from "@/services/apiClient";
import type {
  ClientDetail,
  ClientListResponse,
  ClientCreatePayload,
  ClientUpdatePayload,
  ContactCreatePayload,
  ClientContact,
  LocationCreatePayload,
  ClientLocation,
  NoteCreatePayload,
  ClientNote,
  ClientStatus,
} from "@/types/client";

export interface ClientListParams {
  search?: string;
  status?: ClientStatus;
  page?: number;
  page_size?: number;
}

export const clientService = {
  async list(params: ClientListParams = {}): Promise<ClientListResponse> {
    const { data } = await apiClient.get<ClientListResponse>("/clients", { params });
    return data;
  },

  async getById(id: string): Promise<ClientDetail> {
    const { data } = await apiClient.get<ClientDetail>(`/clients/${id}`);
    return data;
  },

  async create(payload: ClientCreatePayload): Promise<ClientDetail> {
    const { data } = await apiClient.post<ClientDetail>("/clients", payload);
    return data;
  },

  async update(id: string, payload: ClientUpdatePayload): Promise<ClientDetail> {
    const { data } = await apiClient.patch<ClientDetail>(`/clients/${id}`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/clients/${id}`);
  },

  async addContact(clientId: string, payload: ContactCreatePayload): Promise<ClientContact> {
    const { data } = await apiClient.post<ClientContact>(
      `/clients/${clientId}/contacts`,
      payload
    );
    return data;
  },

  async addLocation(clientId: string, payload: LocationCreatePayload): Promise<ClientLocation> {
    const { data } = await apiClient.post<ClientLocation>(
      `/clients/${clientId}/locations`,
      payload
    );
    return data;
  },

  async addNote(clientId: string, payload: NoteCreatePayload): Promise<ClientNote> {
    const { data } = await apiClient.post<ClientNote>(`/clients/${clientId}/notes`, payload);
    return data;
  },

  async updateContact(
    clientId: string,
    contactId: string,
    payload: Partial<ContactCreatePayload>
  ): Promise<ClientContact> {
    const { data } = await apiClient.patch<ClientContact>(
      `/clients/${clientId}/contacts/${contactId}`,
      payload
    );
    return data;
  },

  async deleteContact(clientId: string, contactId: string): Promise<void> {
    await apiClient.delete(`/clients/${clientId}/contacts/${contactId}`);
  },

  async updateLocation(
    clientId: string,
    locationId: string,
    payload: Partial<LocationCreatePayload>
  ): Promise<ClientLocation> {
    const { data } = await apiClient.patch<ClientLocation>(
      `/clients/${clientId}/locations/${locationId}`,
      payload
    );
    return data;
  },

  async deleteLocation(clientId: string, locationId: string): Promise<void> {
    await apiClient.delete(`/clients/${clientId}/locations/${locationId}`);
  },
};
