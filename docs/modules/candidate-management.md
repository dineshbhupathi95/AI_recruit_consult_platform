# Candidate Management

End-to-end candidate recruitment pipeline for staffing agencies.

## Pipeline Flow

```
Create Candidate → Upload Resume → AI Parse → AI Resume Builder (JD)
  → Recruiter Review → Export PDF/DOCX → ATS Score
  → Schedule Interview → AI Interview → Interview Summary
```

## Data Model

| Table | Purpose |
|-------|---------|
| `candidates` | Candidate profile (tenant-scoped) |
| `candidate_applications` | Candidate + job junction with pipeline stage |
| `candidate_documents` | Uploaded resumes (MinIO) |
| `parsed_resumes` | AI-structured resume JSON |
| `resume_versions` | Versioned AI-built resumes |
| `resume_scores` | ATS scoring results |
| `screening_interviews` | AI screening interview transcript & scores |
| `resume_templates` | HTML templates for export |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/candidates` | List / create candidates |
| GET/PATCH | `/candidates/{id}` | Get / update candidate |
| GET/POST | `/applications` | List / create applications |
| GET | `/applications/{id}` | Full pipeline detail |
| POST | `/applications/{id}/resume` | Upload + AI parse resume |
| POST | `/applications/{id}/build-resume` | AI build resume for JD |
| PATCH | `/applications/{id}/resume-versions/{version_id}` | Edit resume JSON |
| POST | `/applications/{id}/resume-versions/{version_id}/review` | Recruiter review |
| POST | `/applications/{id}/score-resume` | ATS score |
| GET | `/applications/{id}/export/{format}` | Export pdf/docx/json |
| POST | `/applications/{id}/schedule-interview` | Schedule AI interview |
| POST | `/applications/{id}/interview/start` | Start interview |
| POST | `/applications/{id}/interview/answer` | Submit answer |
| POST | `/applications/{id}/interview/complete` | Generate summary |

## AI Provider

Configure via environment:

```env
AI_PROVIDER=openai   # or mock for tests
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Set `AI_PROVIDER=mock` for local development without an API key.

## Frontend

- `/candidates` — pipeline list and recent candidates
- `/candidates/new` — create candidate with optional job assignment
- `/applications/:id` — full pipeline wizard UI

## Permissions

- `candidates:read` — view candidates and applications
- `candidates:write` — create, upload, build, score, interview actions
