# Job Requirements Module

## Overview

CRUD for client job requirements with hiring manager and location links, skills, budget, and MinIO file attachments.

## Features

- Full CRUD linked to clients
- Hiring manager selection from client contacts
- Client location selection
- Required/preferred skills (JSON storage)
- Experience range, budget range, notice period
- Employment type, priority, status workflow
- File attachments via MinIO
- Search, filter by status/priority/client
- Dashboard active requirements count
- Audit logging

## API Endpoints

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/api/v1/jobs` | jobs:read |
| POST | `/api/v1/jobs` | jobs:write |
| GET | `/api/v1/jobs/{id}` | jobs:read |
| PATCH | `/api/v1/jobs/{id}` | jobs:write |
| DELETE | `/api/v1/jobs/{id}` | jobs:write |
| POST | `/api/v1/jobs/{id}/attachments` | jobs:write |

## Database Tables

- `job_requirements`
- `job_requirement_attachments`

## Frontend Routes

- `/jobs` — List with search and filters
- `/jobs/new` — Create (supports `?client_id=` preselect)
- `/jobs/:id` — Detail view with attachments
- `/jobs/:id/edit` — Edit form

## Migration

```bash
cd backend && alembic upgrade head
```
