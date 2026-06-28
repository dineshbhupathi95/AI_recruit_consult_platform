import { Link } from "react-router-dom";
import { Briefcase } from "lucide-react";
import { JobPriorityBadge, JobStatusBadge } from "@/components/jobs/JobBadges";
import { ViewActionButton } from "@/components/ui/ViewActionButton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EMPLOYMENT_TYPE_LABELS, type JobSummary } from "@/types/job";

export function JobTable({ jobs }: { jobs: JobSummary[] }) {
  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center">
        <Briefcase className="mb-4 h-12 w-12 text-muted-foreground/50" />
        <h3 className="text-lg font-medium">No job requirements yet</h3>
        <p className="mt-1 text-sm text-muted-foreground">Create a requirement linked to a client.</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Job Title</TableHead>
          <TableHead>Client</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Priority</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Experience</TableHead>
          <TableHead className="w-12 text-center">View</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {jobs.map((job) => (
          <TableRow key={job.id}>
            <TableCell>
              <Link to={`/jobs/${job.id}`} className="font-medium hover:text-primary hover:underline">
                {job.title}
              </Link>
              {job.location_text && <p className="text-xs text-muted-foreground">{job.location_text}</p>}
            </TableCell>
            <TableCell>
              <Link to={`/clients/${job.client_id}`} className="text-sm hover:underline">{job.client_name}</Link>
            </TableCell>
            <TableCell className="text-muted-foreground">{EMPLOYMENT_TYPE_LABELS[job.employment_type]}</TableCell>
            <TableCell><JobPriorityBadge priority={job.priority} /></TableCell>
            <TableCell><JobStatusBadge status={job.status} /></TableCell>
            <TableCell className="text-muted-foreground">
              {job.experience_min_years != null || job.experience_max_years != null
                ? `${job.experience_min_years ?? 0}–${job.experience_max_years ?? "∞"} yrs`
                : "—"}
            </TableCell>
            <TableCell className="text-center">
              <ViewActionButton to={`/jobs/${job.id}`} label="View requirement" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
