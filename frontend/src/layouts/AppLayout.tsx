import { Briefcase, LayoutDashboard, LogOut, Moon, Sun, Users } from "lucide-react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/utils/cn";
import { useTheme } from "@/hooks/useTheme";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/clients", label: "Clients", icon: Briefcase, disabled: true },
  { to: "/candidates", label: "Candidates", icon: Users, disabled: true },
];

export function AppLayout() {
  const navigate = useNavigate();
  const { user, tenant, refreshToken, clearAuth } = useAuthStore();
  const { theme, toggleTheme } = useTheme();

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
          {navItems.map(({ to, label, icon: Icon, disabled }) => (
            <Link
              key={to}
              to={disabled ? "#" : to}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                disabled
                  ? "cursor-not-allowed text-muted-foreground/50"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
              onClick={(e) => disabled && e.preventDefault()}
            >
              <Icon className="h-4 w-4" />
              {label}
              {disabled && (
                <span className="ml-auto text-[10px] uppercase tracking-wide text-muted-foreground">
                  Soon
                </span>
              )}
            </Link>
          ))}
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
