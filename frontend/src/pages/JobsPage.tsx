import { useQuery } from "@tanstack/react-query";
import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { JobTable } from "@/components/jobs/JobTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { jobService } from "@/services/jobService";
import type { JobPriority, JobStatus } from "@/types/job";

export function JobsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<JobStatus | "">("");
  const [priority, setPriority] = useState<JobPriority | "">("");
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ["jobs", { search, status, priority, page }],
    queryFn: () => jobService.list({ search: search || undefined, status: status || undefined, priority: priority || undefined, page, page_size: 20 }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Job Requirements</h1>
          <p className="text-muted-foreground">Manage open positions and client requirements</p>
        </div>
        <Link to="/jobs/new"><Button><Plus className="h-4 w-4" />Add Requirement</Button></Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Requirements</CardTitle>
          <CardDescription>{data ? `${data.total} requirement${data.total !== 1 ? "s" : ""}` : "Loading..."}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="pl-9" placeholder="Search jobs or clients..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <Select className="sm:w-40" value={status} onChange={(e) => { setStatus(e.target.value as JobStatus | ""); setPage(1); }}>
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="open">Open</option>
              <option value="on_hold">On Hold</option>
              <option value="filled">Filled</option>
              <option value="closed">Closed</option>
            </Select>
            <Select className="sm:w-40" value={priority} onChange={(e) => { setPriority(e.target.value as JobPriority | ""); setPage(1); }}>
              <option value="">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </Select>
          </div>
          {isLoading && <div className="py-12 text-center text-muted-foreground">Loading...</div>}
          {error && <div className="py-12 text-center text-destructive">Failed to load requirements</div>}
          {data && <JobTable jobs={data.items} />}
          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4">
              <p className="text-sm text-muted-foreground">Page {data.page} of {data.total_pages}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
                <Button variant="outline" size="sm" disabled={page >= data.total_pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
