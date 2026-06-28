export type EmploymentType = "full_time" | "part_time" | "contract" | "temporary" | "internship";
export type JobPriority = "low" | "medium" | "high" | "urgent";
export type JobStatus = "draft" | "open" | "on_hold" | "filled" | "closed" | "cancelled";

export interface JobAttachment {
  id: string;
  job_requirement_id: string;
  file_name: string;
  file_key: string;
  content_type: string | null;
  file_size_bytes: number | null;
  created_at: string;
}

export interface JobSummary {
  id: string;
  client_id: string;
  client_name: string;
  title: string;
  employment_type: EmploymentType;
  priority: JobPriority;
  status: JobStatus;
  location_text: string | null;
  experience_min_years: number | null;
  experience_max_years: number | null;
  required_skills_count: number;
  hiring_manager_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobDetail {
  id: string;
  tenant_id: string;
  client_id: string;
  client_name: string;
  hiring_manager_id: string | null;
  hiring_manager_name: string | null;
  client_location_id: string | null;
  client_location_name: string | null;
  title: string;
  experience_min_years: number | null;
  experience_max_years: number | null;
  budget_min: string | null;
  budget_max: string | null;
  budget_currency: string;
  notice_period_days: number | null;
  location_text: string | null;
  employment_type: EmploymentType;
  priority: JobPriority;
  status: JobStatus;
  description: string | null;
  required_skills: string[];
  preferred_skills: string[];
  attachments: JobAttachment[];
  created_at: string;
  updated_at: string;
}

export interface JobListResponse {
  items: JobSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobCreatePayload {
  client_id: string;
  title: string;
  hiring_manager_id?: string;
  client_location_id?: string;
  experience_min_years?: number;
  experience_max_years?: number;
  budget_min?: number;
  budget_max?: number;
  budget_currency?: string;
  notice_period_days?: number;
  location_text?: string;
  employment_type?: EmploymentType;
  priority?: JobPriority;
  status?: JobStatus;
  description?: string;
  required_skills?: string[];
  preferred_skills?: string[];
}

export type JobUpdatePayload = Partial<Omit<JobCreatePayload, "client_id">>;

export const EMPLOYMENT_TYPE_LABELS: Record<EmploymentType, string> = {
  full_time: "Full Time",
  part_time: "Part Time",
  contract: "Contract",
  temporary: "Temporary",
  internship: "Internship",
};

export const JOB_PRIORITY_LABELS: Record<JobPriority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  draft: "Draft",
  open: "Open",
  on_hold: "On Hold",
  filled: "Filled",
  closed: "Closed",
  cancelled: "Cancelled",
};
