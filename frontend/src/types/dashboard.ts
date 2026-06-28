export interface DashboardStatCard {
  label: string;
  value: number | string;
  change_percent?: number | null;
  trend?: string | null;
}

export interface PipelineStage {
  stage: string;
  label: string;
  count: number;
  color?: string | null;
}

export interface TodayInterviewItem {
  id: string;
  candidate_name: string;
  job_title: string;
  client_name: string;
  scheduled_at: string;
  status: string;
}

export interface RecentActivityItem {
  id: string;
  action: string;
  resource_type: string;
  description: string;
  created_at: string;
}

export interface ScoreSummary {
  average: number | null;
  count: number;
  label: string;
}

export interface DashboardOverview {
  stats: DashboardStatCard[];
  pipeline: PipelineStage[];
  todays_interviews: TodayInterviewItem[];
  recent_activity: RecentActivityItem[];
  resume_score: ScoreSummary;
  interview_score: ScoreSummary;
  clients_by_status: Record<string, number>;
}
