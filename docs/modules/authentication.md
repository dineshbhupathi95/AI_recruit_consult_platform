# Authentication Module

## Overview

Multi-tenant JWT authentication with RBAC for recruitment consultancy organizations.

## Features

- Tenant (organization) registration
- Recruiter login with JWT access + refresh tokens
- Token refresh rotation
- Logout and logout-all sessions
- RBAC with roles and permissions
- Password change with session revocation
- Audit-ready schema (audit_logs table)

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register consultancy + admin | Public |
| POST | `/api/v1/auth/login` | Login recruiter | Public |
| POST | `/api/v1/auth/refresh` | Refresh tokens | Public |
| POST | `/api/v1/auth/logout` | Revoke refresh token | Public |
| POST | `/api/v1/auth/logout-all` | Revoke all sessions | Required |
| GET | `/api/v1/auth/me` | Current user profile | Required |
| POST | `/api/v1/auth/change-password` | Change password | Required |

## Default Roles

- **admin** — Full permissions within tenant
- **recruiter** — Clients, jobs, candidates, interviews, analytics

## Database Tables

- `tenants` — Multi-tenant organizations
- `users` — Recruiter accounts
- `roles` / `permissions` / `role_permissions` / `user_roles` — RBAC
- `refresh_tokens` — Secure session management
- `audit_logs` — Compliance audit trail

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Frontend Routes

- `/login` — Sign in
- `/register` — Create consultancy account
- `/dashboard` — Protected dashboard (placeholder for Module 2)
