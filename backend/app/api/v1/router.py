"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import auth, candidates, clients, dashboard, jobs, resume_templates, settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(dashboard.router)
api_router.include_router(jobs.router)
api_router.include_router(candidates.router)
api_router.include_router(resume_templates.router)
api_router.include_router(settings.router)
