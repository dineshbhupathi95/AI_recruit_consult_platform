import { Building2, ClipboardList, FileText, LayoutDashboard, LogOut, Moon, Settings, Sun, Users } from "lucide-react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/utils/cn";
import { useTheme } from "@/hooks/useTheme";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/clients", label: "Clients", icon: Building2 },
  { to: "/jobs", label: "Requirements", icon: ClipboardList },
  { to: "/candidates", label: "Candidates", icon: Users },
  { to: "/templates", label: "Templates", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings, adminOnly: true },
];

export function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, tenant, refreshToken, clearAuth } = useAuthStore();
  const { theme, toggleTheme } = useTheme();

  const permissions = user?.permissions ?? [];
  const roles = user?.roles.map((r) => r.name) ?? [];
  const isAdmin = roles.includes("admin") || permissions.includes("settings:read");

  const handleLogout = async () => {
    if (refreshToken) {
      try {
        await authService.logout(refreshToken);
      } catch {
        // Clear local session even if server logout fails
      }
    }
    clearAuth();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-border bg-card">
        <div className="flex h-16 items-center border-b border-border px-6">
          <div>
            <p className="text-sm font-semibold">AI Recruit</p>
            <p className="truncate text-xs text-muted-foreground">{tenant?.name}</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-4">
          {navItems
            .filter((item) => !item.adminOnly || isAdmin)
            .map(({ to, label, icon: Icon }) => {
            const isActive = location.pathname === to || location.pathname.startsWith(`${to}/`);
            return (
              <Link
                key={to}
                to={to}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border p-4">
          <div className="mb-3 truncate text-sm">
            <p className="font-medium">{user?.full_name}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button variant="outline" className="flex-1" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      <main className="pl-64">
        <div className="mx-auto max-w-7xl p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
