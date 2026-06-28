import { useMutation } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { formValuesToPayload, JobForm } from "@/components/jobs/JobForm";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { jobFormSchema, type JobFormValues } from "@/forms/jobSchemas";
import { jobService } from "@/services/jobService";
import { getErrorMessage } from "@/services/apiClient";

export function JobCreatePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedClientId = searchParams.get("client_id") ?? "";
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: jobService.create,
    onSuccess: (job) => navigate(`/jobs/${job.id}`),
    onError: (err) => setError(getErrorMessage(err)),
  });

  const handleSubmit = async (values: JobFormValues) => {
    setError(null);
    jobFormSchema.parse(values);
    await mutation.mutateAsync(formValuesToPayload(values));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/jobs"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Job Requirement</h1>
          <p className="text-muted-foreground">Create an open position for a client</p>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Requirement Details</CardTitle>
          <CardDescription>Link to a client and define the role</CardDescription>
        </CardHeader>
        <CardContent>
          {error && <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>}
          <JobForm
            defaultValues={{ client_id: preselectedClientId }}
            lockClient={!!preselectedClientId}
            onSubmit={handleSubmit}
            isSubmitting={mutation.isPending}
            submitLabel="Create Requirement"
            onCancel={() => navigate(preselectedClientId ? `/clients/${preselectedClientId}` : "/jobs")}
          />
        </CardContent>
      </Card>
    </div>
  );
}
