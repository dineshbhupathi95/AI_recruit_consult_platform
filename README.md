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

## Environment

All API calls use one base URL from `src/config/api.ts`, driven by:

```bash
# frontend/.env (copy from .env.example)
VITE_API_BASE_URL=http://localhost:8000
```

Do **not** include `/api/v1` — the app appends that automatically.

**Vercel:** Project → Settings → Environment Variables → `VITE_API_BASE_URL` = your backend URL (e.g. `https://api.example.com`), then redeploy.

**Docker:** `VITE_API_BASE_URL` is set in root `docker-compose.yml` for the frontend service.


```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Ensure `.env` exists at the project root (`cp .env.example .env` from repo root).

For **local** migrations (outside Docker), start Postgres first and use `localhost` in `DATABASE_URL`:

```bash
# From project root — start Postgres only
docker compose up -d postgres

# In .env, use the localhost DATABASE_URL line (see .env.example)
# DATABASE_URL=postgresql+asyncpg://recruit:recruit_secret@localhost:5432/recruit_platform

cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

When using **Docker Compose** for the full stack, migrations run automatically on backend startup.

### Free AI testing (no API keys)

- **Mock provider** — Settings → Mock → Save (instant, no setup)
- **Ollama** — local open-source models: `docker compose --profile ollama up -d` then `docker compose exec ollama ollama pull llama3.2`
- See `docs/modules/settings.md` for configuration details

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
| Dashboard | ✅ Complete |
| Client Management | ✅ Complete |
| Job Requirements | ✅ Complete |
| Candidate Management | ✅ Complete |
| Settings (AI Provider) | ✅ Complete |

## Architecture

Multi-tenant SaaS with Repository Pattern, Service Layer, and Dependency Injection throughout.
