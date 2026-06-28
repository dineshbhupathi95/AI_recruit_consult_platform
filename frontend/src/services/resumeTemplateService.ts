import { apiClient } from "@/services/apiClient";
import type {
  ResumeTemplateCreatePayload,
  ResumeTemplateDetail,
  ResumeTemplateListResponse,
  ResumeTemplateUpdatePayload,
} from "@/types/resumeTemplate";

export const resumeTemplateService = {
  async list(): Promise<ResumeTemplateListResponse> {
    const { data } = await apiClient.get<ResumeTemplateListResponse>("/resume-templates");
    return data;
  },

  async get(id: string): Promise<ResumeTemplateDetail> {
    const { data } = await apiClient.get<ResumeTemplateDetail>(`/resume-templates/${id}`);
    return data;
  },

  async create(payload: ResumeTemplateCreatePayload): Promise<ResumeTemplateDetail> {
    const { data } = await apiClient.post<ResumeTemplateDetail>("/resume-templates", payload);
    return data;
  },

  async upload(
    file: File,
    options: { name?: string; description?: string; is_default?: boolean } = {}
  ): Promise<ResumeTemplateDetail> {
    const form = new FormData();
    form.append("file", file);
    if (options.name) form.append("name", options.name);
    if (options.description) form.append("description", options.description);
    if (options.is_default) form.append("is_default", "true");
    const { data } = await apiClient.post<ResumeTemplateDetail>("/resume-templates/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async update(id: string, payload: ResumeTemplateUpdatePayload): Promise<ResumeTemplateDetail> {
    const { data } = await apiClient.patch<ResumeTemplateDetail>(`/resume-templates/${id}`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/resume-templates/${id}`);
  },

  async fetchPreviewHtml(id: string): Promise<string> {
    const { data } = await apiClient.get<string>(`/resume-templates/${id}/preview`, {
      params: { mode: "sample" },
      responseType: "text",
    });
    return data;
  },

  async fetchSourceBlob(id: string): Promise<Blob> {
    const response = await apiClient.get(`/resume-templates/${id}/source`, {
      responseType: "blob",
    });
    return response.data as Blob;
  },
};
