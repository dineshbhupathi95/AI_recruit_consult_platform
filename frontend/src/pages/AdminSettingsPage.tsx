import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { SettingsPage } from "@/pages/SettingsPage";

function canAccessSettings(permissions: string[], roles: string[]) {
  return permissions.includes("settings:read") || roles.includes("admin");
}

export function AdminSettingsPage() {
  const user = useAuthStore((s) => s.user);
  const permissions = user?.permissions ?? [];
  const roles = user?.roles.map((r) => r.name) ?? [];

  if (!canAccessSettings(permissions, roles)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <SettingsPage />;
}
