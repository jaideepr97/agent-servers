# OpenCode A2A Agent Server

Agent server for OpenCode that serves a dynamic A2A agent card at `/.well-known/agent-card.json`.

## Required Fields

| Field | Type | What it's for | How we get it |
|-------|------|---------------|---------------|
| `name` | string | Display name in list/detail | Env var `A2A_TITLE` (default: `"OpenCode"`) |
| `description` | string | Shown in detail page, list descriptions | Base from env var `A2A_DESCRIPTION` + dynamic agent names from `GET /api/agent`, provider names from `GET /api/provider`, model count from `GET /api/model` |
| `version` | string | Shown in detail page | Env var `A2A_VERSION` (default: `"1.0.0"`) |
| `url` | string | Base service endpoint URL | Env var `A2A_PUBLIC_URL` (default: `"http://127.0.0.1:8000"`) |
| `skills` | array | Skills table in detail page | Dynamic from `GET /api/agent` — each non-hidden agent maps to a skill (see below) |

## Optional Fields — Configurable (env vars)

| Field | Type | What we render | How we get it |
|-------|------|----------------|---------------|
| `provider.organization` | string | Provider badge/label | Env var `A2A_PROVIDER_ORG` (default: `"Red Hat"`) |
| `provider.url` | string | Provider link | Env var `A2A_PROVIDER_URL` (default: `"https://redhat.com"`) |
| `documentationUrl` | string | Docs link in detail page | Env var `A2A_DOCUMENTATION_URL` (default: `"https://opencode.ai/docs"`) |
| `iconUrl` | string | Agent icon/avatar | Env var `A2A_ICON_URL` (default: `"https://opencode.ai/favicon-v3.svg"`) |

## Optional Fields — Hardcoded

These are facts about OpenCode that don't change per deployment.

| Field | Type | What we render | Value |
|-------|------|----------------|-------|
| `defaultInputModes` | string[] | I/O modes display | `["text/plain", "application/octet-stream"]` |
| `defaultOutputModes` | string[] | I/O modes display | `["text/plain", "application/json"]` |
| `capabilities.streaming` | bool | Capability badge | `false` — changes to `true` with A2A protocol support (RHAIENG-5826) |
| `capabilities.pushNotifications` | bool | Capability badge | `false` |
| `capabilities.extensions` | array | Extension list | `[]` — populated with A2A protocol support (RHAIENG-5826) |

## Skill Fields

Each non-hidden agent from `GET /api/agent` maps to a skill:

| Field | Type | What we render | How we get it |
|-------|------|----------------|---------------|
| `skills[].id` | string | Skill identifier | `"opencode.{agent.id}"` from `GET /api/agent` |
| `skills[].name` | string | Skill display name | `"OpenCode {agent.id}"` (titlecased) from `GET /api/agent` |
| `skills[].description` | string | Skill description | `agent.description` from `GET /api/agent` |
| `skills[].tags` | string[] | Skill tags/chips | `["opencode", "coding", agent.mode]` from `GET /api/agent` |
| `skills[].examples` | string[] | Example prompts | Hardcoded per skill (e.g. `"Fix the failing unit test in auth.py"`) |
| `skills[].inputModes` | string[] | Skill I/O | Hardcoded: `["text/plain", "application/octet-stream"]` |
| `skills[].outputModes` | string[] | Skill I/O | Hardcoded: `["text/plain", "application/json"]` |

`skills[].parameters` is not included — OpenCode skills accept free-text prompts, not structured parameters. The opencode-a2a upstream project also omits this field.

Fallback when `opencode serve` is unreachable: single skill `opencode.chat`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCODE_BASE_URL` | `http://127.0.0.1:4096` | URL of `opencode serve` |
| `A2A_HOST` | `127.0.0.1` | Server listen host |
| `A2A_PORT` | `8000` | Server listen port |
| `A2A_PUBLIC_URL` | `http://127.0.0.1:8000` | Public URL in the agent card |
| `A2A_TITLE` | `OpenCode` | Agent name |
| `A2A_DESCRIPTION` | `AI-powered coding assistant` | Base description |
| `A2A_VERSION` | `1.0.0` | Agent version |
| `A2A_DOCUMENTATION_URL` | `https://opencode.ai/docs` | Documentation link |
| `A2A_PROVIDER_ORG` | `Red Hat` | Provider organization |
| `A2A_PROVIDER_URL` | `https://redhat.com` | Provider URL |
| `A2A_ICON_URL` | `https://opencode.ai/favicon-v3.svg` | Agent icon URL |
