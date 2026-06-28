import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { formValuesToPayload, JobForm, jobToFormValues } from "@/components/jobs/JobForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { jobFormSchema, type JobFormValues } from "@/forms/jobSchemas";
import { jobService } from "@/services/jobService";
import { getErrorMessage } from "@/services/apiClient";

export function JobEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: job, isLoading } = useQuery({
    queryKey: ["jobs", id],
    queryFn: () => jobService.getById(id!),
    enabled: !!id,
  });

  const mutation = useMutation({
    mutationFn: (values: JobFormValues) => {
      const payload = formValuesToPayload(values);
      const { client_id: _, ...updatePayload } = payload;
      return jobService.update(id!, updatePayload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      navigate(`/jobs/${id}`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  if (isLoading) return <div className="py-12 text-center text-muted-foreground">Loading...</div>;
  if (!job) return <div className="py-12 text-center text-destructive">Job not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to={`/jobs/${id}`}><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Requirement</h1>
          <p className="text-muted-foreground">{job.title}</p>
        </div>
      </div>
      <Card>
        <CardHeader><CardTitle>Update Details</CardTitle></CardHeader>
        <CardContent>
          {error && <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>}
          <JobForm
            defaultValues={jobToFormValues(job)}
            lockClient
            onSubmit={async (values) => { setError(null); jobFormSchema.parse(values); await mutation.mutateAsync(values); }}
            isSubmitting={mutation.isPending}
            submitLabel="Save Changes"
            onCancel={() => navigate(`/jobs/${id}`)}
          />
        </CardContent>
      </Card>
    </div>
  );
}
