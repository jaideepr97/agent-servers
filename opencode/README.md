# OpenCode A2A Server

Serves an [A2A agent card](https://a2a-protocol.org/latest/specification/) at `/.well-known/agent-card.json` for OpenCode, enabling discovery by the RHOAI agent catalog and [Kagenti](https://kagenti.github.io/.github/).

## Prerequisites

- Python 3.11+
- [OpenCode](https://opencode.ai) installed

## Quick Start

### 1. Start OpenCode serve

```bash
cd /path/to/your/project
opencode serve
```

This starts OpenCode's API on `http://127.0.0.1:4096`.

### 2. Start the A2A server

```bash
cd agent-servers/opencode
pip install -e .
opencode-a2a
```

```
OpenCode A2A Server
  Server:       http://127.0.0.1:8000
  OpenCode:     http://127.0.0.1:4096
  Agent card:   http://127.0.0.1:8000/.well-known/agent-card.json
  Swagger:      http://127.0.0.1:8000/docs
```

### 3. Verify

```bash
curl http://localhost:8000/.well-known/agent-card.json
curl http://localhost:8000/health
```

## CLI Flags

```bash
opencode-a2a [OPTIONS]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--port` | Server port | `8000` |
| `--opencode-url` | OpenCode serve URL | `http://127.0.0.1:4096` |
| `--env-file` | Path to env file | `.env` |

Examples:

```bash
# Custom port
opencode-a2a --port 9000

# Custom OpenCode URL
opencode-a2a --opencode-url http://localhost:4096

# Both
opencode-a2a --port 9000 --opencode-url http://localhost:4096
```

## Environment Variables

All settings can be configured via environment variables. CLI flags override env vars.

See [`.env.example`](.env.example) for all available variables and their defaults.

```bash
cp .env.example .env
# Edit .env with your values
opencode-a2a
```

## Agent Card

The server dynamically builds the A2A agent card by querying OpenCode's API (`/api/agent`, `/api/provider`, `/api/model`) and combining it with configuration from env vars.

For a full breakdown of every field in the agent card — required, optional, hardcoded, and dynamic — see [AGENT_CARD_FIELDS.md](AGENT_CARD_FIELDS.md).

## Endpoints

| Path | Description |
|------|-------------|
| `/.well-known/agent-card.json` | A2A agent card |
| `/.well-known/agent.json` | Same card (older A2A spec path) |
| `/health` | Proxied health check from OpenCode serve |
| `/docs` | Swagger UI |

## References

- [A2A Agent Card spec](https://a2a-protocol.org/latest/specification/)
- [opencode-a2a](https://github.com/Intelligent-Internet/opencode-a2a) — full A2A implementation we referenced
- [OpenCode](https://opencode.ai)
