import { apiClient } from "@/services/apiClient";
import type { JobCreatePayload, JobDetail, JobListResponse, JobUpdatePayload } from "@/types/job";
import type { JobPriority, JobStatus } from "@/types/job";

export interface JobListParams {
  search?: string;
  status?: JobStatus;
  client_id?: string;
  priority?: JobPriority;
  page?: number;
  page_size?: number;
}

export const jobService = {
  async list(params: JobListParams = {}): Promise<JobListResponse> {
    const { data } = await apiClient.get<JobListResponse>("/jobs", { params });
    return data;
  },

  async getById(id: string): Promise<JobDetail> {
    const { data } = await apiClient.get<JobDetail>(`/jobs/${id}`);
    return data;
  },

  async create(payload: JobCreatePayload): Promise<JobDetail> {
    const { data } = await apiClient.post<JobDetail>("/jobs", payload);
    return data;
  },

  async update(id: string, payload: JobUpdatePayload): Promise<JobDetail> {
    const { data } = await apiClient.patch<JobDetail>(`/jobs/${id}`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/jobs/${id}`);
  },

  async uploadAttachment(jobId: string, file: File): Promise<void> {
    const formData = new FormData();
    formData.append("file", file);
    await apiClient.post(`/jobs/${jobId}/attachments`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};
