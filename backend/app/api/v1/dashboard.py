"""Dashboard API endpoints."""

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DashboardServiceDep
from app.schemas.dashboard import DashboardOverviewResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Dashboard overview",
    description="Get dashboard metrics, pipeline, and recent activity.",
)
async def get_dashboard_overview(
    current_user: CurrentUser,
    dashboard_service: DashboardServiceDep,
) -> DashboardOverviewResponse:
    current_user.require_permission("analytics:read")
    return await dashboard_service.get_overview(current_user.tenant_id)
