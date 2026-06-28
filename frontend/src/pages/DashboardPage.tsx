import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Briefcase,
  Building2,
  Calendar,
  FileText,
  TrendingUp,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { dashboardService } from "@/services/dashboardService";
import { useAuthStore } from "@/store/authStore";
import { CLIENT_STATUS_LABELS, type ClientStatus } from "@/types/client";

const STAT_ICONS: Record<string, typeof Briefcase> = {
  "Active Clients": Building2,
  "Total Clients": Building2,
  "Active Requirements": Briefcase,
  Candidates: Users,
  "Pending Interviews": Calendar,
  "Hiring Managers": Users,
};

export function DashboardPage() {
  const { user, tenant } = useAuthStore();

  const { data: overview, isLoading } = useQuery({
    queryKey: ["dashboard", "overview"],
    queryFn: dashboardService.getOverview,
  });

  const primaryStats = overview?.stats.slice(0, 4) ?? [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.first_name}. Overview for {tenant?.name}.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                </CardHeader>
                <CardContent>
                  <div className="h-8 w-16 animate-pulse rounded bg-muted" />
                </CardContent>
              </Card>
            ))
          : primaryStats.map(({ label, value }) => {
              const Icon = STAT_ICONS[label] ?? Briefcase;
              return (
                <Card key={label}>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">{label}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{value}</div>
                  </CardContent>
                </Card>
              );
            })}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Recruitment Pipeline
            </CardTitle>
            <CardDescription>Candidate flow across stages</CardDescription>
          </CardHeader>
          <CardContent>
            {overview?.pipeline.length ? (
              <div className="space-y-3">
                {overview.pipeline.map((stage) => (
                  <div key={stage.stage} className="flex items-center gap-4">
                    <span className="w-24 text-sm text-muted-foreground">{stage.label}</span>
                    <div className="flex-1">
                      <div className="h-2 overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{
                            width: stage.count > 0 ? `${Math.min(stage.count * 10, 100)}%` : "0%",
                          }}
                        />
                      </div>
                    </div>
                    <span className="w-8 text-right text-sm font-medium">{stage.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Pipeline data will populate once candidates are added.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Scores
            </CardTitle>
            <CardDescription>Resume and interview averages</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">{overview?.resume_score.label}</p>
              <p className="text-2xl font-bold">
                {overview?.resume_score.average != null
                  ? `${overview.resume_score.average.toFixed(1)}%`
                  : "—"}
              </p>
              <p className="text-xs text-muted-foreground">
                {overview?.resume_score.count ?? 0} scored
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{overview?.interview_score.label}</p>
              <p className="text-2xl font-bold">
                {overview?.interview_score.average != null
                  ? `${overview.interview_score.average.toFixed(1)}%`
                  : "—"}
              </p>
              <p className="text-xs text-muted-foreground">
                {overview?.interview_score.count ?? 0} completed
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Today&apos;s Interviews
            </CardTitle>
            <CardDescription>Scheduled AI screening sessions</CardDescription>
          </CardHeader>
          <CardContent>
            {overview?.todays_interviews.length ? (
              <div className="space-y-3">
                {overview.todays_interviews.map((interview) => (
                  <div
                    key={interview.id}
                    className="flex items-center justify-between rounded-md border border-border p-3"
                  >
                    <div>
                      <p className="font-medium">{interview.candidate_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {interview.job_title} · {interview.client_name}
                      </p>
                    </div>
                    <Badge variant="outline">{interview.status}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No interviews scheduled for today.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Activity
            </CardTitle>
            <CardDescription>Latest actions across your organization</CardDescription>
          </CardHeader>
          <CardContent>
            {overview?.recent_activity.length ? (
              <div className="space-y-3">
                {overview.recent_activity.map((item) => (
                  <div key={item.id} className="flex items-start gap-3 text-sm">
                    <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary" />
                    <div className="flex-1">
                      <p>{item.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(item.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No recent activity.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Clients by Status</CardTitle>
            <CardDescription>Distribution of client companies</CardDescription>
          </CardHeader>
          <CardContent>
            {overview && Object.keys(overview.clients_by_status).length > 0 ? (
              <div className="flex flex-wrap gap-3">
                {Object.entries(overview.clients_by_status).map(([status, count]) => (
                  <div
                    key={status}
                    className="flex items-center gap-2 rounded-md border border-border px-3 py-2"
                  >
                    <span className="text-sm">
                      {CLIENT_STATUS_LABELS[status as ClientStatus] ?? status}
                    </span>
                    <Badge variant="secondary">{count}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  No clients yet. Create your first client to get started.
                </p>
                <Link to="/clients/new">
                  <Button>Add Client</Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Complete these steps to begin recruiting</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center gap-3 rounded-md border border-border p-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                1
              </span>
              <Link to="/clients" className="hover:underline">
                Manage client companies
              </Link>
              {(overview?.stats.find((s) => s.label === "Total Clients")?.value as number) > 0 && (
                <Badge variant="success" className="ml-auto">
                  Done
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 rounded-md border border-border p-3 opacity-60">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs">2</span>
              <Link to="/jobs" className="hover:underline">Add job requirements</Link>
            </div>
            <div className="flex items-center gap-3 rounded-md border border-border p-3 opacity-60">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs">3</span>
              <span>Create and screen candidates</span>
              <span className="ml-auto text-[10px] uppercase tracking-wide text-muted-foreground">Next module</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
