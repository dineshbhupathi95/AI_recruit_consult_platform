"""AI provider definitions and dynamic form field schemas."""

from typing import Any, Literal

FieldType = Literal["text", "password", "url", "number", "select"]

SECRET_FIELD_TYPES: frozenset[str] = frozenset({"password"})

AI_PROVIDER_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "openai",
        "label": "OpenAI",
        "description": "OpenAI Chat Completions API (GPT-4o, GPT-4o-mini, etc.)",
        "env_prefix": "OPENAI",
        "fields": [
            {
                "key": "openai_api_key",
                "label": "API Key",
                "type": "password",
                "required": True,
                "placeholder": "sk-...",
                "env_var": "OPENAI_API_KEY",
            },
            {
                "key": "openai_model",
                "label": "Model",
                "type": "text",
                "required": True,
                "default": "gpt-4o-mini",
                "env_var": "OPENAI_MODEL",
            },
            {
                "key": "openai_base_url",
                "label": "Base URL",
                "type": "url",
                "required": True,
                "default": "https://api.openai.com/v1",
                "env_var": "OPENAI_BASE_URL",
            },
        ],
    },
    {
        "id": "azure_openai",
        "label": "Azure OpenAI",
        "description": "Microsoft Azure OpenAI Service",
        "env_prefix": "AZURE_OPENAI",
        "fields": [
            {
                "key": "azure_openai_api_key",
                "label": "API Key",
                "type": "password",
                "required": True,
                "env_var": "AZURE_OPENAI_API_KEY",
            },
            {
                "key": "azure_openai_endpoint",
                "label": "Endpoint URL",
                "type": "url",
                "required": True,
                "placeholder": "https://your-resource.openai.azure.com",
                "env_var": "AZURE_OPENAI_ENDPOINT",
            },
            {
                "key": "azure_openai_deployment",
                "label": "Deployment Name",
                "type": "text",
                "required": True,
                "env_var": "AZURE_OPENAI_DEPLOYMENT",
            },
            {
                "key": "azure_openai_api_version",
                "label": "API Version",
                "type": "text",
                "required": True,
                "default": "2024-02-15-preview",
                "env_var": "AZURE_OPENAI_API_VERSION",
            },
        ],
    },
    {
        "id": "deepseek",
        "label": "DeepSeek",
        "description": "DeepSeek OpenAI-compatible API",
        "env_prefix": "DEEPSEEK",
        "fields": [
            {
                "key": "deepseek_api_key",
                "label": "API Key",
                "type": "password",
                "required": True,
                "env_var": "DEEPSEEK_API_KEY",
            },
            {
                "key": "deepseek_model",
                "label": "Model",
                "type": "text",
                "required": True,
                "default": "deepseek-chat",
                "env_var": "DEEPSEEK_MODEL",
            },
            {
                "key": "deepseek_base_url",
                "label": "Base URL",
                "type": "url",
                "required": True,
                "default": "https://api.deepseek.com/v1",
                "env_var": "DEEPSEEK_BASE_URL",
            },
        ],
    },
    {
        "id": "groq",
        "label": "Groq",
        "description": "Groq fast inference API — free tier available (Llama, Mixtral, Gemma)",
        "env_prefix": "GROQ",
        "fields": [
            {
                "key": "groq_api_key",
                "label": "API Key",
                "type": "password",
                "required": True,
                "placeholder": "gsk_...",
                "env_var": "GROQ_API_KEY",
            },
            {
                "key": "groq_model",
                "label": "Model",
                "type": "text",
                "required": True,
                "default": "llama-3.1-8b-instant",
                "placeholder": "llama-3.3-70b-versatile, mixtral-8x7b-32768",
                "env_var": "GROQ_MODEL",
            },
            {
                "key": "groq_base_url",
                "label": "Base URL",
                "type": "url",
                "required": True,
                "default": "https://api.groq.com/openai/v1",
                "env_var": "GROQ_BASE_URL",
            },
        ],
    },
    {
        "id": "gemini",
        "label": "Google Gemini",
        "description": "Google Gemini API (OpenAI-compatible endpoint)",
        "env_prefix": "GEMINI",
        "fields": [
            {
                "key": "gemini_api_key",
                "label": "API Key",
                "type": "password",
                "required": True,
                "placeholder": "AIza...",
                "env_var": "GEMINI_API_KEY",
            },
            {
                "key": "gemini_model",
                "label": "Model",
                "type": "text",
                "required": True,
                "default": "gemini-2.0-flash",
                "env_var": "GEMINI_MODEL",
            },
            {
                "key": "gemini_base_url",
                "label": "Base URL",
                "type": "url",
                "required": True,
                "default": "https://generativelanguage.googleapis.com/v1beta/openai",
                "env_var": "GEMINI_BASE_URL",
            },
        ],
    },
    {
        "id": "ollama",
        "label": "Ollama (Local Open Source)",
        "description": "Run Llama, Mistral, Phi, etc. locally — free, no API key. Works with Ollama or LM Studio.",
        "env_prefix": "OLLAMA",
        "fields": [
            {
                "key": "ollama_base_url",
                "label": "Base URL",
                "type": "url",
                "required": True,
                "default": "http://localhost:11434/v1",
                "placeholder": "http://localhost:11434/v1",
                "env_var": "OLLAMA_BASE_URL",
            },
            {
                "key": "ollama_model",
                "label": "Model",
                "type": "text",
                "required": True,
                "default": "llama3.2",
                "placeholder": "llama3.2, mistral, phi3, ...",
                "env_var": "OLLAMA_MODEL",
            },
            {
                "key": "ollama_api_key",
                "label": "API Key (optional)",
                "type": "password",
                "required": False,
                "placeholder": "Leave empty for local Ollama",
                "env_var": "OLLAMA_API_KEY",
            },
        ],
    },
    {
        "id": "mock",
        "label": "Mock (Testing)",
        "description": "Deterministic fake responses — no server or API key required",
        "env_prefix": "MOCK",
        "fields": [],
    },
]

COMMON_AI_FIELDS: list[dict[str, Any]] = [
    {
        "key": "ai_request_timeout_seconds",
        "label": "Request Timeout (seconds)",
        "type": "number",
        "required": False,
        "default": 120,
        "env_var": "AI_REQUEST_TIMEOUT_SECONDS",
    },
]


def get_provider_definition(provider_id: str) -> dict[str, Any] | None:
    for provider in AI_PROVIDER_DEFINITIONS:
        if provider["id"] == provider_id:
            return provider
    return None


def all_secret_keys() -> set[str]:
    keys: set[str] = set()
    for provider in AI_PROVIDER_DEFINITIONS:
        for field in provider["fields"]:
            if field["type"] in SECRET_FIELD_TYPES:
                keys.add(field["key"])
    return keys
