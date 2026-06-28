import { apiClient } from "@/services/apiClient";
import type {
  ApplicationDetail,
  ApplicationListResponse,
  BuildResumePayload,
  Candidate,
  CandidateCreatePayload,
  CandidateListResponse,
  InterviewQuestionResponse,
  ResumeBuildContext,
  ResumeScore,
  ResumeVersion,
  ScreeningInterview,
} from "@/types/candidate";

export interface CandidateListParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ApplicationListParams {
  candidate_id?: string;
  job_requirement_id?: string;
  pipeline_stage?: string;
  page?: number;
  page_size?: number;
}

export const candidateService = {
  async listCandidates(params: CandidateListParams = {}): Promise<CandidateListResponse> {
    const { data } = await apiClient.get<CandidateListResponse>("/candidates", { params });
    return data;
  },

  async getCandidate(id: string): Promise<Candidate> {
    const { data } = await apiClient.get<Candidate>(`/candidates/${id}`);
    return data;
  },

  async createCandidate(payload: CandidateCreatePayload): Promise<Candidate> {
    const { data } = await apiClient.post<Candidate>("/candidates", payload);
    return data;
  },

  async listApplications(params: ApplicationListParams = {}): Promise<ApplicationListResponse> {
    const { data } = await apiClient.get<ApplicationListResponse>("/applications", { params });
    return data;
  },

  async getApplication(id: string): Promise<ApplicationDetail> {
    const { data } = await apiClient.get<ApplicationDetail>(`/applications/${id}`);
    return data;
  },

  async createApplication(payload: {
    candidate_id: string;
    job_requirement_id: string;
    recruiter_notes?: string;
  }): Promise<ApplicationDetail> {
    const { data } = await apiClient.post<ApplicationDetail>("/applications", payload);
    return data;
  },

  async uploadResume(applicationId: string, file: File): Promise<ApplicationDetail> {
    const form = new FormData();
    form.append("file", file);
    const { data } = await apiClient.post<ApplicationDetail>(
      `/applications/${applicationId}/resume`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return data;
  },

  async getResumeBuildContext(applicationId: string): Promise<ResumeBuildContext> {
    const { data } = await apiClient.get<ResumeBuildContext>(
      `/applications/${applicationId}/resume-build-context`
    );
    return data;
  },

  async buildResume(applicationId: string, payload: BuildResumePayload): Promise<ResumeVersion> {
    const { data } = await apiClient.post<ResumeVersion>(
      `/applications/${applicationId}/build-resume`,
      payload
    );
    return data;
  },

  async reviewResume(
    applicationId: string,
    versionId: string,
    decision: string,
    notes?: string
  ): Promise<ResumeVersion> {
    const { data } = await apiClient.post<ResumeVersion>(
      `/applications/${applicationId}/resume-versions/${versionId}/review`,
      { decision, notes }
    );
    return data;
  },

  async scoreResume(applicationId: string, versionId?: string): Promise<ResumeScore> {
    const { data } = await apiClient.post<ResumeScore>(
      `/applications/${applicationId}/score-resume`,
      null,
      { params: versionId ? { version_id: versionId } : undefined }
    );
    return data;
  },

  async exportResume(applicationId: string, format: "pdf" | "docx" | "json" | "html", versionId?: string) {
    const response = await apiClient.get(
      `/applications/${applicationId}/export/${format}`,
      {
        params: versionId ? { version_id: versionId } : undefined,
        responseType: "blob",
      }
    );
    return response;
  },

  async scheduleInterview(
    applicationId: string,
    payload: {
      scheduled_at?: string;
      duration_minutes?: number;
      difficulty?: string;
    }
  ): Promise<ScreeningInterview> {
    const { data } = await apiClient.post<ScreeningInterview>(
      `/applications/${applicationId}/schedule-interview`,
      payload
    );
    return data;
  },

  async startInterview(applicationId: string): Promise<InterviewQuestionResponse> {
    const { data } = await apiClient.post<InterviewQuestionResponse>(
      `/applications/${applicationId}/interview/start`
    );
    return data;
  },

  async submitAnswer(applicationId: string, answer: string): Promise<InterviewQuestionResponse> {
    const { data } = await apiClient.post<InterviewQuestionResponse>(
      `/applications/${applicationId}/interview/answer`,
      { answer }
    );
    return data;
  },

  async completeInterview(applicationId: string): Promise<ScreeningInterview> {
    const { data } = await apiClient.post<ScreeningInterview>(
      `/applications/${applicationId}/interview/complete`
    );
    return data;
  },
};
