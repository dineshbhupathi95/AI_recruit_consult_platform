import { apiClient } from "@/services/apiClient";
import type { DashboardOverview } from "@/types/dashboard";

export const dashboardService = {
  async getOverview(): Promise<DashboardOverview> {
    const { data } = await apiClient.get<DashboardOverview>("/dashboard/overview");
    return data;
  },
};
