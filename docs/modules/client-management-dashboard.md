# Client Management & Dashboard Modules

## Overview

Production-ready client company management with contacts, hiring managers, locations, and notes. Dashboard provides real-time metrics aggregated from available data.

## Client Management Features

- CRUD for client companies
- Contact management (general, hiring manager, primary)
- Location management with headquarters flag
- Notes with audit trail
- Search and status filtering
- Pagination
- Soft delete
- Multi-tenant isolation
- RBAC permission checks (`clients:read`, `clients:write`)
- Audit logging for all mutations

## Dashboard Features

- Stat cards: active clients, total clients, requirements, candidates, interviews, hiring managers
- Recruitment pipeline stages (ready for candidate module)
- Resume and interview score summaries
- Today's interviews (ready for interview module)
- Recent activity from audit logs
- Clients by status breakdown

## API Endpoints

### Clients

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/clients` | List clients | clients:read |
| POST | `/api/v1/clients` | Create client | clients:write |
| GET | `/api/v1/clients/{id}` | Get client detail | clients:read |
| PATCH | `/api/v1/clients/{id}` | Update client | clients:write |
| DELETE | `/api/v1/clients/{id}` | Delete client | clients:write |
| POST | `/api/v1/clients/{id}/contacts` | Add contact | clients:write |
| PATCH | `/api/v1/clients/{id}/contacts/{contact_id}` | Update contact | clients:write |
| DELETE | `/api/v1/clients/{id}/contacts/{contact_id}` | Delete contact | clients:write |
| POST | `/api/v1/clients/{id}/locations` | Add location | clients:write |
| PATCH | `/api/v1/clients/{id}/locations/{location_id}` | Update location | clients:write |
| DELETE | `/api/v1/clients/{id}/locations/{location_id}` | Delete location | clients:write |
| POST | `/api/v1/clients/{id}/notes` | Add note | clients:write |

### Dashboard

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/dashboard/overview` | Dashboard metrics | analytics:read |

## Database Tables

- `clients` — Client companies
- `client_contacts` — Contacts and hiring managers
- `client_locations` — Office locations
- `client_notes` — Internal notes

## Frontend Routes

- `/dashboard` — Dashboard overview
- `/clients` — Client list with search
- `/clients/new` — Create client
- `/clients/:id` — Client detail with contacts, locations, notes

## Running Tests

```bash
cd backend
pytest tests/integration/test_clients_api.py tests/integration/test_dashboard_api.py -v
```
