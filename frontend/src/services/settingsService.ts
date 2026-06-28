import { apiClient } from "@/services/apiClient";
import type {
  SettingsSchemaResponse,
  TenantSettingsResponse,
  TestAIConnectionResponse,
  UpdateTenantSettingsRequest,
} from "@/types/settings";

export const settingsService = {
  async getSchema(): Promise<SettingsSchemaResponse> {
    const { data } = await apiClient.get<SettingsSchemaResponse>("/settings/schema");
    return data;
  },

  async getSettings(): Promise<TenantSettingsResponse> {
    const { data } = await apiClient.get<TenantSettingsResponse>("/settings");
    return data;
  },

  async updateSettings(payload: UpdateTenantSettingsRequest): Promise<TenantSettingsResponse> {
    const { data } = await apiClient.put<TenantSettingsResponse>("/settings", payload);
    return data;
  },

  async testAIConnection(): Promise<TestAIConnectionResponse> {
    const { data } = await apiClient.post<TestAIConnectionResponse>("/settings/test-ai");
    return data;
  },
};
