import { Link } from "react-router-dom";
import { Users } from "lucide-react";
import { BuiltResumePreviewButton } from "@/components/candidates/BuiltResumePreviewButton";
import { ViewActionButton } from "@/components/ui/ViewActionButton";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ApplicationSummary } from "@/types/candidate";
import { PIPELINE_STAGE_LABELS } from "@/types/candidate";

interface ApplicationTableProps {
  applications: ApplicationSummary[];
}

function formatScore(value: string | null): string | null {
  if (value == null) return null;
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return Number.isInteger(num) ? String(num) : num.toFixed(1);
}

export function ApplicationTable({ applications }: ApplicationTableProps) {
  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center">
        <Users className="mb-4 h-12 w-12 text-muted-foreground/50" />
        <h3 className="text-lg font-medium">No pipeline applications yet</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Create a candidate and assign them to a job requirement to start the pipeline.
        </p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Candidate</TableHead>
          <TableHead>Job</TableHead>
          <TableHead>Client</TableHead>
          <TableHead>Stage</TableHead>
          <TableHead>Resume</TableHead>
          <TableHead>Score</TableHead>
          <TableHead>Interview</TableHead>
          <TableHead className="w-12 text-center">View</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {applications.map((app) => {
          const resumeScore = formatScore(app.latest_score);
          const interviewScore = formatScore(app.interview_overall_score);

          return (
            <TableRow key={app.id}>
              <TableCell>
                <Link to={`/applications/${app.id}`} className="font-medium hover:underline">
                  {app.candidate_name}
                </Link>
              </TableCell>
              <TableCell className="text-muted-foreground">{app.job_title}</TableCell>
              <TableCell className="text-muted-foreground">{app.client_name}</TableCell>
              <TableCell>
                <Badge variant="outline">{PIPELINE_STAGE_LABELS[app.pipeline_stage]}</Badge>
              </TableCell>
              <TableCell>
                {app.latest_resume_version_id ? (
                  <div className="flex items-center gap-1">
                    <BuiltResumePreviewButton
                      applicationId={app.id}
                      versionId={app.latest_resume_version_id}
                      candidateName={app.candidate_name}
                    />
                    <span className="text-xs text-muted-foreground">
                      v{app.resume_version_count}
                      {app.latest_built_resume_status
                        ? ` · ${app.latest_built_resume_status.replace(/_/g, " ")}`
                        : ""}
                    </span>
                  </div>
                ) : app.has_parsed_resume ? (
                  <span className="text-sm text-muted-foreground">Uploaded only</span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell>
                {resumeScore != null ? (
                  <span className="font-semibold tabular-nums">{resumeScore}</span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell>
                {interviewScore != null ? (
                  <span className="font-semibold tabular-nums">{interviewScore}</span>
                ) : app.interview_status ? (
                  <Badge variant="outline">{app.interview_status.replace(/_/g, " ")}</Badge>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell className="text-center">
                <ViewActionButton to={`/applications/${app.id}`} label="View pipeline" />
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
