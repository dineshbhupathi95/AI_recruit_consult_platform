export interface ResumeTemplateSummary {
  id: string;
  name: string;
  description: string | null;
  is_default: boolean;
  is_system: boolean;
  source_type: string;
  source_file_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeTemplateDetail extends ResumeTemplateSummary {
  tenant_id: string | null;
  html_template: string;
  css_styles: string;
  config: Record<string, unknown>;
}

export interface ResumeTemplateListResponse {
  items: ResumeTemplateSummary[];
  total: number;
}

export interface ResumeTemplateCreatePayload {
  name: string;
  description?: string;
  html_template: string;
  css_styles?: string;
  is_default?: boolean;
}

export interface ResumeTemplateUpdatePayload {
  name?: string;
  description?: string;
  html_template?: string;
  css_styles?: string;
  is_default?: boolean;
}
