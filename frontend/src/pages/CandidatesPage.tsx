import { useQuery } from "@tanstack/react-query";
import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { ApplicationTable } from "@/components/candidates/ApplicationTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { candidateService } from "@/services/candidateService";
import type { PipelineStage } from "@/types/candidate";
import { PIPELINE_STAGE_LABELS } from "@/types/candidate";

export function CandidatesPage() {
  const [search, setSearch] = useState("");
  const [stage, setStage] = useState<PipelineStage | "">("");
  const [page, setPage] = useState(1);

  const { data: applications, isLoading: appsLoading, error: appsError } = useQuery({
    queryKey: ["applications", { stage, page }],
    queryFn: () =>
      candidateService.listApplications({
        pipeline_stage: stage || undefined,
        page,
        page_size: 20,
      }),
  });

  const { data: candidates } = useQuery({
    queryKey: ["candidates", { search }],
    queryFn: () => candidateService.listCandidates({ search: search || undefined, page_size: 5 }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">
            Manage candidates through the AI recruitment pipeline
          </p>
        </div>
        <Link to="/candidates/new">
          <Button>
            <Plus className="h-4 w-4" />
            Add Candidate
          </Button>
        </Link>
      </div>

      {candidates && candidates.total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Candidates</CardTitle>
            <CardDescription>{candidates.total} total in directory</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {candidates.items.map((c) => (
                <li key={c.id} className="flex justify-between">
                  <span className="font-medium">{c.full_name}</span>
                  <span className="text-muted-foreground">{c.email ?? c.current_company ?? "—"}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Recruitment Pipeline</CardTitle>
          <CardDescription>
            {applications
              ? `${applications.total} application${applications.total !== 1 ? "s" : ""} in pipeline`
              : "Loading..."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                className="pl-9"
                placeholder="Search candidates..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Select
              className="sm:w-48"
              value={stage}
              onChange={(e) => {
                setStage(e.target.value as PipelineStage | "");
                setPage(1);
              }}
            >
              <option value="">All Stages</option>
              {(Object.keys(PIPELINE_STAGE_LABELS) as PipelineStage[]).map((s) => (
                <option key={s} value={s}>{PIPELINE_STAGE_LABELS[s]}</option>
              ))}
            </Select>
          </div>

          {appsLoading && (
            <div className="py-12 text-center text-muted-foreground">Loading pipeline...</div>
          )}
          {appsError && (
            <div className="py-12 text-center text-destructive">Failed to load applications</div>
          )}
          {applications && <ApplicationTable applications={applications.items} />}

          {applications && applications.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4">
              <p className="text-sm text-muted-foreground">
                Page {applications.page} of {applications.total_pages}
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= applications.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
