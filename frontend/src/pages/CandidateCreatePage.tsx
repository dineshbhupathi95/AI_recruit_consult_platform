import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { getErrorMessage } from "@/services/apiClient";
import { candidateService } from "@/services/candidateService";
import { jobService } from "@/services/jobService";

export function CandidateCreatePage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [company, setCompany] = useState("");
  const [jobId, setJobId] = useState("");
  const [notes, setNotes] = useState("");

  const { data: jobs } = useQuery({
    queryKey: ["jobs", "open"],
    queryFn: () => jobService.list({ status: "open", page_size: 100 }),
  });

  const mutation = useMutation({
    mutationFn: candidateService.createCandidate,
    onSuccess: async (candidate) => {
      if (jobId) {
        const apps = await candidateService.listApplications({ candidate_id: candidate.id });
        const app = apps.items[0];
        if (app) {
          navigate(`/applications/${app.id}`);
          return;
        }
      }
      navigate("/candidates");
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    mutation.mutate({
      first_name: firstName,
      last_name: lastName,
      email: email || undefined,
      phone: phone || undefined,
      current_company: company || undefined,
      notes: notes || undefined,
      job_requirement_id: jobId || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/candidates")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Candidate</h1>
          <p className="text-muted-foreground">Add a candidate and optionally start a job pipeline</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Candidate Details</CardTitle>
          <CardDescription>Basic profile information</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
          )}
          <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input id="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input id="lastName" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="company">Current Company</Label>
              <Input id="company" value={company} onChange={(e) => setCompany(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="job">Job Requirement</Label>
              <Select id="job" value={jobId} onChange={(e) => setJobId(e.target.value)}>
                <option value="">No job (add later)</option>
                {jobs?.items.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} — {job.client_name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
            </div>
            <div className="sm:col-span-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Creating..." : "Create Candidate"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
