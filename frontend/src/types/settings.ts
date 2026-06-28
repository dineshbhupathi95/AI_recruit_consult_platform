export type SettingFieldType = "text" | "password" | "url" | "number" | "select";

export interface SettingFieldSchema {
  key: string;
  label: string;
  type: SettingFieldType;
  required: boolean;
  default?: string | number | null;
  placeholder?: string | null;
  env_var?: string | null;
  options?: Array<{ value: string; label: string }> | null;
}

export interface AIProviderSchema {
  id: string;
  label: string;
  description: string;
  env_prefix: string;
  fields: SettingFieldSchema[];
}

export interface SettingsSchemaResponse {
  ai_providers: AIProviderSchema[];
  common_ai_fields: SettingFieldSchema[];
  secret_mask: string;
}

export interface SettingValueResponse {
  key: string;
  value: string | number | null;
  is_set: boolean;
  is_secret: boolean;
  source: "tenant" | "environment" | "default";
}

export interface TenantSettingsResponse {
  ai_provider: string;
  values: SettingValueResponse[];
  updated_at: string | null;
}

export interface UpdateTenantSettingsRequest {
  ai_provider: string;
  values: Record<string, string | number | null>;
}

export interface TestAIConnectionResponse {
  success: boolean;
  message: string;
  provider: string;
}
