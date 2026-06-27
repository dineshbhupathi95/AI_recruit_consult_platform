import { useQuery } from "@tanstack/react-query";
import { Briefcase, Calendar, FileText, Users } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";

const stats = [
  { label: "Active Requirements", value: "0", icon: Briefcase },
  { label: "Candidates", value: "0", icon: Users },
  { label: "Pending Interviews", value: "0", icon: Calendar },
  { label: "Resume Scores", value: "—", icon: FileText },
];

export function DashboardPage() {
  const { user, tenant } = useAuthStore();

  useQuery({
    queryKey: ["me"],
    queryFn: authService.getMe,
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.first_name}. Overview for {tenant?.name}.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">{label}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
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
              <span>Create your first client</span>
              <span className="ml-auto text-xs text-muted-foreground">Coming in Module 2</span>
            </div>
            <div className="flex items-center gap-3 rounded-md border border-border p-3 opacity-60">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs">
                2
              </span>
              <span>Add a job requirement</span>
            </div>
            <div className="flex items-center gap-3 rounded-md border border-border p-3 opacity-60">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs">
                3
              </span>
              <span>Create and screen candidates</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Profile</CardTitle>
            <CardDescription>Account and permissions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Role</span>
              <span className="font-medium capitalize">{user?.roles[0]?.name ?? "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Permissions</span>
              <span className="font-medium">{user?.permissions.length ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tenant</span>
              <span className="font-medium">{tenant?.slug}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
