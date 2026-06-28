import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "@/layouts/AppLayout";
import { CandidateCreatePage } from "@/pages/CandidateCreatePage";
import { CandidatesPage } from "@/pages/CandidatesPage";
import { AdminSettingsPage } from "@/pages/AdminSettingsPage";
import { ApplicationPipelinePage } from "@/pages/ApplicationPipelinePage";
import { ClientCreatePage } from "@/pages/ClientCreatePage";
import { ClientDetailPage } from "@/pages/ClientDetailPage";
import { ClientEditPage } from "@/pages/ClientEditPage";
import { ClientsPage } from "@/pages/ClientsPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { JobCreatePage } from "@/pages/JobCreatePage";
import { JobDetailPage } from "@/pages/JobDetailPage";
import { JobEditPage } from "@/pages/JobEditPage";
import { JobsPage } from "@/pages/JobsPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { ResumeTemplatesPage } from "@/pages/ResumeTemplatesPage";
import { ProtectedRoute, PublicRoute } from "@/routes/ProtectedRoute";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/clients" element={<ClientsPage />} />
              <Route path="/clients/new" element={<ClientCreatePage />} />
              <Route path="/clients/:id/edit" element={<ClientEditPage />} />
              <Route path="/clients/:id" element={<ClientDetailPage />} />
              <Route path="/jobs" element={<JobsPage />} />
              <Route path="/jobs/new" element={<JobCreatePage />} />
              <Route path="/jobs/:id/edit" element={<JobEditPage />} />
              <Route path="/jobs/:id" element={<JobDetailPage />} />
              <Route path="/candidates" element={<CandidatesPage />} />
              <Route path="/candidates/new" element={<CandidateCreatePage />} />
              <Route path="/applications/:id" element={<ApplicationPipelinePage />} />
              <Route path="/templates" element={<ResumeTemplatesPage />} />
              <Route path="/settings" element={<AdminSettingsPage />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
