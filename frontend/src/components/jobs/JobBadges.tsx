import type { JobPriority, JobStatus } from "@/types/job";
import { JOB_PRIORITY_LABELS, JOB_STATUS_LABELS } from "@/types/job";
import { Badge } from "@/components/ui/badge";

const PRIORITY_VARIANTS: Record<JobPriority, "secondary" | "default" | "warning" | "destructive"> = {
  low: "secondary",
  medium: "default",
  high: "warning",
  urgent: "destructive",
};

const STATUS_VARIANTS: Record<JobStatus, "secondary" | "success" | "warning" | "default" | "destructive" | "outline"> = {
  draft: "secondary",
  open: "success",
  on_hold: "warning",
  filled: "default",
  closed: "outline",
  cancelled: "destructive",
};

export function JobPriorityBadge({ priority }: { priority: JobPriority }) {
  return <Badge variant={PRIORITY_VARIANTS[priority]}>{JOB_PRIORITY_LABELS[priority]}</Badge>;
}

export function JobStatusBadge({ status }: { status: JobStatus }) {
  return <Badge variant={STATUS_VARIANTS[status]}>{JOB_STATUS_LABELS[status]}</Badge>;
}
