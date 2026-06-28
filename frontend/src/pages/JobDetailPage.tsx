import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Building2, Edit, Paperclip, Trash2, User } from "lucide-react";
import { useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { JobPriorityBadge, JobStatusBadge } from "@/components/jobs/JobBadges";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { jobService } from "@/services/jobService";
import { EMPLOYMENT_TYPE_LABELS } from "@/types/job";

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: job, isLoading } = useQuery({
    queryKey: ["jobs", id],
    queryFn: () => jobService.getById(id!),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => jobService.delete(id!),
    onSuccess: () => navigate("/jobs"),
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => jobService.uploadAttachment(id!, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs", id] }),
  });

  if (isLoading) return <div className="py-12 text-center text-muted-foreground">Loading...</div>;
  if (!job) return <div className="py-12 text-center text-destructive">Job not found</div>;

  const formatBudget = () => {
    if (job.budget_min == null && job.budget_max == null) return "—";
    const currency = job.budget_currency;
    if (job.budget_min != null && job.budget_max != null) return `${currency} ${job.budget_min} – ${job.budget_max}`;
    if (job.budget_min != null) return `${currency} ${job.budget_min}+`;
    return `Up to ${currency} ${job.budget_max}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <Link to="/jobs"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-3xl font-bold tracking-tight">{job.title}</h1>
              <JobStatusBadge status={job.status} />
              <JobPriorityBadge priority={job.priority} />
            </div>
            <Link to={`/clients/${job.client_id}`} className="text-muted-foreground hover:underline">{job.client_name}</Link>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/jobs/${id}/edit`}><Button variant="outline"><Edit className="h-4 w-4" />Edit</Button></Link>
          <Button variant="destructive" size="icon" onClick={() => { if (confirm("Delete this requirement?")) deleteMutation.mutate(); }}><Trash2 className="h-4 w-4" /></Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm">{job.description ?? "No description provided."}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Details</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <DetailRow label="Employment" value={EMPLOYMENT_TYPE_LABELS[job.employment_type]} />
            <DetailRow label="Experience" value={job.experience_min_years != null || job.experience_max_years != null ? `${job.experience_min_years ?? 0}–${job.experience_max_years ?? "∞"} years` : "—"} />
            <DetailRow label="Budget" value={formatBudget()} />
            <DetailRow label="Notice Period" value={job.notice_period_days != null ? `${job.notice_period_days} days` : "—"} />
            <DetailRow label="Location" value={job.client_location_name ?? job.location_text ?? "—"} />
            <div className="flex items-start gap-2 pt-1">
              <User className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div><p className="text-muted-foreground">Hiring Manager</p><p className="font-medium">{job.hiring_manager_name ?? "—"}</p></div>
            </div>
            <div className="flex items-start gap-2">
              <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div><p className="text-muted-foreground">Client</p><Link to={`/clients/${job.client_id}`} className="font-medium hover:underline">{job.client_name}</Link></div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Required Skills</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {job.required_skills.length ? job.required_skills.map((s) => <Badge key={s} variant="default">{s}</Badge>) : <p className="text-sm text-muted-foreground">None specified</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Preferred Skills</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {job.preferred_skills.length ? job.preferred_skills.map((s) => <Badge key={s} variant="secondary">{s}</Badge>) : <p className="text-sm text-muted-foreground">None specified</p>}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2"><Paperclip className="h-5 w-5" />Attachments</CardTitle>
            <CardDescription>Job description documents and files</CardDescription>
          </div>
          <div>
            <input ref={fileInputRef} type="file" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) uploadMutation.mutate(f); e.target.value = ""; }} />
            <Button size="sm" variant="outline" disabled={uploadMutation.isPending} onClick={() => fileInputRef.current?.click()}>
              {uploadMutation.isPending ? "Uploading..." : "Upload File"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {job.attachments.length ? (
            <ul className="space-y-2">
              {job.attachments.map((a) => (
                <li key={a.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
                  <span>{a.file_name}</span>
                  <span className="text-muted-foreground">{a.file_size_bytes ? `${Math.round(a.file_size_bytes / 1024)} KB` : ""}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">No attachments uploaded.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (<div className="flex justify-between gap-4"><span className="text-muted-foreground">{label}</span><span className="font-medium text-right">{value}</span></div>);
}
