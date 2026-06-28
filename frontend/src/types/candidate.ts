export type PipelineStage = "sourced" | "screening" | "interview" | "submitted" | "placed";
export type ApplicationStatus = "active" | "on_hold" | "rejected" | "withdrawn" | "placed";
export type ParseStatus = "pending" | "processing" | "completed" | "failed";
export type ResumeVersionStatus = "draft" | "pending_review" | "approved" | "needs_changes" | "rejected";
export type RecruiterReviewDecision =
  | "accept"
  | "reject"
  | "needs_more_interview"
  | "needs_resume_changes"
  | "submit_to_client";
export type InterviewStatus = "scheduled" | "in_progress" | "completed" | "cancelled";
export type HireRecommendation = "strong_hire" | "hire" | "hold" | "reject";

export interface Candidate {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  current_company: string | null;
  current_ctc: string | null;
  expected_ctc: string | null;
  notice_period_days: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateListResponse {
  items: Candidate[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CandidateCreatePayload {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  current_company?: string;
  current_ctc?: number;
  expected_ctc?: number;
  notice_period_days?: number;
  notes?: string;
  job_requirement_id?: string;
}

export interface ParsedResume {
  id: string;
  application_id: string;
  status: ParseStatus;
  structured_data: Record<string, unknown> | null;
  error_message: string | null;
  parsed_at: string | null;
}

export interface ResumeVersion {
  id: string;
  application_id: string;
  version_number: number;
  status: ResumeVersionStatus;
  template_id: string | null;
  template_name?: string | null;
  content_json: Record<string, unknown>;
  recruiter_review_decision: RecruiterReviewDecision | null;
  recruiter_review_notes: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeScore {
  id: string;
  application_id: string;
  resume_version_id: string | null;
  overall_score: string;
  keyword_match: string | null;
  skill_match: string | null;
  experience_match: string | null;
  semantic_similarity: string | null;
  formatting_score: string | null;
  grammar_score: string | null;
  achievements_score: string | null;
  missing_keywords: string[];
  suggestions: string[];
  improvement_areas: string[];
  created_at: string;
}

export interface ScreeningInterview {
  id: string;
  application_id: string;
  status: InterviewStatus;
  scheduled_at: string | null;
  duration_minutes: number;
  difficulty: string;
  coding_required: boolean;
  behavioral: boolean;
  technical: boolean;
  language: string;
  timezone: string;
  interview_link: string | null;
  transcript: Array<Record<string, unknown>>;
  summary: string | null;
  technical_score: string | null;
  coding_score: string | null;
  communication_score: string | null;
  confidence_score: string | null;
  problem_solving_score: string | null;
  recommendation: HireRecommendation | null;
  completed_at: string | null;
}

export interface ApplicationSummary {
  id: string;
  candidate_id: string;
  candidate_name: string;
  job_requirement_id: string;
  job_title: string;
  client_name: string;
  pipeline_stage: PipelineStage;
  status: ApplicationStatus;
  has_parsed_resume: boolean;
  resume_version_count: number;
  latest_resume_version_id: string | null;
  latest_built_resume_status: ResumeVersionStatus | null;
  latest_score: string | null;
  interview_status: InterviewStatus | null;
  interview_overall_score: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail {
  id: string;
  tenant_id: string;
  candidate_id: string;
  candidate: Candidate;
  job_requirement_id: string;
  job_title: string;
  client_name: string;
  job_description: string | null;
  job_experience_min_years: number | null;
  job_experience_max_years: number | null;
  pipeline_stage: PipelineStage;
  status: ApplicationStatus;
  recruiter_notes: string | null;
  parsed_resume: ParsedResume | null;
  resume_versions: ResumeVersion[];
  resume_scores: ResumeScore[];
  screening_interview: ScreeningInterview | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationListResponse {
  items: ApplicationSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ResumeExperienceInput {
  company: string;
  title: string;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  bullets?: string[];
}

export interface ResumeEducationInput {
  institution: string;
  degree: string;
  field?: string | null;
  graduation_year?: string | null;
  start_year?: string | null;
}

export interface TimelineGap {
  label: string;
  from_date: string;
  to_date: string;
  months: number;
  suggestion: string;
}

export interface GapStrategyOption {
  id: string;
  label: string;
  description: string;
}

export interface ResumeBuildContext {
  job_experience_min_years: number | null;
  job_experience_max_years: number | null;
  candidate_total_experience_years: number;
  experience_shortfall_years: number | null;
  timeline_gaps: TimelineGap[];
  gap_strategy_options: GapStrategyOption[];
  recommendations: string[];
  default_summary: string | null;
  default_skills: string[];
  default_experience: ResumeExperienceInput[];
  default_education: ResumeEducationInput[];
  templates: Array<{
    id: string;
    name: string;
    description: string | null;
    is_default: boolean;
    is_system: boolean;
    source_type: string;
    source_file_name: string | null;
  }>;
  default_template_id: string | null;
}

export interface BuildResumePayload {
  template_id: string;
  recruiter_notes?: string;
  gap_strategy?: string;
  target_total_experience_years?: number;
  summary?: string;
  skills?: string[];
  experience?: ResumeExperienceInput[];
  education?: ResumeEducationInput[];
  training_entry?: ResumeExperienceInput;
}

export interface InterviewQuestionResponse {
  question: string;
  interview_status: InterviewStatus;
  question_number: number;
  question_type: "mcq" | "scenario" | "coding";
  options: Array<{ id: string; text: string }>;
  phase_label?: string | null;
  total_questions: number;
  is_complete: boolean;
}

export const PIPELINE_STAGE_LABELS: Record<PipelineStage, string> = {
  sourced: "Sourced",
  screening: "Screening",
  interview: "Interview",
  submitted: "Submitted",
  placed: "Placed",
};

export const PIPELINE_STEPS = [
  { key: "create", label: "Create Candidate" },
  { key: "upload", label: "Upload Resume" },
  { key: "parse", label: "AI Parse" },
  { key: "build", label: "AI Resume Builder" },
  { key: "review", label: "Recruiter Review" },
  { key: "export", label: "Export PDF/DOCX" },
  { key: "score", label: "ATS Score" },
  { key: "schedule", label: "Schedule Interview" },
  { key: "interview", label: "AI Interview" },
  { key: "summary", label: "Interview Summary" },
] as const;
