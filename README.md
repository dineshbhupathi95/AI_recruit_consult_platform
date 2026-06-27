# AI Recruit Consult Platform

Enterprise AI Recruitment Consultancy SaaS Platform for recruitment agencies.

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, TailwindCSS, Shadcn UI, TanStack Query, Zustand
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Celery
- **Storage:** MinIO
- **Deployment:** Docker, Docker Compose

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Start all services:

```bash
docker compose up --build
```

3. Access:
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001

## Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test
```

## Modules

| Module | Status |
|--------|--------|
| Authentication | ✅ Complete |
| Dashboard | Pending |
| Client Management | Pending |
| Job Requirements | Pending |
| Candidate Management | Pending |

## Architecture

Multi-tenant SaaS with Repository Pattern, Service Layer, and Dependency Injection throughout.
