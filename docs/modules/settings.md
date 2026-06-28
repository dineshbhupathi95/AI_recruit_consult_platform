# Settings

Admin UI and API for tenant-scoped configuration that overrides environment variables.

## Access

- Permissions: `settings:read`, `settings:write`
- Tenant **admin** role has both permissions
- Frontend: `/settings` (visible in sidebar for admins)

## AI Provider Configuration

Supported providers (dynamic form fields per provider):

| Provider | Fields |
|----------|--------|
| OpenAI | API Key, Model, Base URL |
| Azure OpenAI | API Key, Endpoint, Deployment, API Version |
| DeepSeek | API Key, Model, Base URL |
| Groq | API Key, Model, Base URL |
| Google Gemini | API Key, Model, Base URL |
| **Ollama (Local)** | Base URL, Model, API Key (optional) |
| Mock | None (instant testing, no server) |

Common field: **Request Timeout (seconds)**

## Free local testing (no API keys)

### Option 1: Mock provider (fastest)

1. Settings → Provider **Mock (Testing)** → Save
2. Full pipeline works with deterministic fake AI responses

### Option 2: Ollama (real open-source models)

Run Llama, Mistral, Phi, etc. on your machine for free.

**With Docker Compose:**

```bash
docker compose --profile ollama up -d
docker compose exec ollama ollama pull llama3.2
```

**Settings UI:**

- Provider: **Ollama (Local Open Source)**
- Base URL: `http://ollama:11434/v1` (Docker) or `http://localhost:11434/v1` (local backend)
- Model: `llama3.2` (or `mistral`, `phi3`, `llama3.2:1b` for smaller/faster)
- API Key: leave empty

**Without Docker** — install [Ollama](https://ollama.com), then:

```bash
ollama pull llama3.2
ollama serve
```

Also works with **LM Studio** (enable Local Server, use `http://localhost:1234/v1`).

Recommended small models for dev: `llama3.2:1b`, `phi3:mini`, `mistral:7b`.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings/schema` | Provider definitions and form field schemas |
| GET | `/settings` | Current tenant settings (secrets masked) |
| PUT | `/settings` | Save tenant settings |
| POST | `/settings/test-ai` | Test AI provider connection |

## Priority

1. **Tenant settings** (saved via admin UI, encrypted at rest)
2. **Environment variables** (`.env` / Docker Compose)
3. **Schema defaults**

## Environment Variables

Still supported as fallbacks and for infrastructure:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
AI_REQUEST_TIMEOUT_SECONDS=120
```

## Security

- API keys and secrets are encrypted at rest using `APP_SECRET_KEY`
- API responses mask secrets as `********`
- Leave password fields blank on save to keep existing values
