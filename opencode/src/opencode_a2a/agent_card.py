"""
Dynamic A2A agent card builder for OpenCode.

Builds the agent card by combining:
- Dynamic data from opencode serve (/api/agent, /api/provider, /api/model)
- Configurable values from env vars (name, version, provider, urls)
- Hardcoded values that describe OpenCode's actual capabilities

Inspired by https://github.com/Intelligent-Internet/opencode-a2a which
hardcodes all card fields from settings. We extend that by dynamically
fetching agents, providers, and models from opencode serve so the card
reflects the live state of the deployment.
"""

from __future__ import annotations

import asyncio

from .config import Settings
from .opencode_client import OpencodeClient

# ---------------------------------------------------------------------------
# Hardcoded constants
# ---------------------------------------------------------------------------
# These describe what OpenCode accepts and returns. OpenCode processes plain
# text and binary input, returns text and structured JSON. Same values used
# by opencode-a2a upstream. Not configurable because they are facts about
# OpenCode, not deployment choices.

DEFAULT_INPUT_MODES = ["text/plain", "application/octet-stream"]
DEFAULT_OUTPUT_MODES = ["text/plain", "application/json"]

# Example prompts per built-in agent. opencode-a2a upstream also hardcodes
# examples per skill since opencode serve does not expose example prompts
# through its API.
SKILL_EXAMPLES: dict[str, list[str]] = {
    "build": [
        "Fix the failing unit test in auth.py",
        "Refactor the database module to use connection pooling",
        "Add input validation to the REST API endpoints",
    ],
    "plan": [
        "Plan the implementation for adding OAuth2 support",
        "Design the architecture for a new notification service",
    ],
    "explore": [
        "Find all API endpoint definitions in the project",
        "Where is the database connection configured?",
        "Search for all usages of the User model",
    ],
    "general": [
        "Explain what this repository does.",
        "Summarize the API endpoints in this project.",
        "Investigate why the CI pipeline is failing",
    ],
}

# Used when opencode serve is unreachable.
FALLBACK_SKILL = {
    "id": "opencode.chat",
    "name": "OpenCode Chat",
    "description": "AI coding assistant for code generation, editing, and review",
    "tags": ["opencode", "coding", "assistant"],
    "examples": SKILL_EXAMPLES.get("build", []),
    "inputModes": list(DEFAULT_INPUT_MODES),
    "outputModes": list(DEFAULT_OUTPUT_MODES),
}


# ---------------------------------------------------------------------------
# Skills — dynamic from GET /api/agent
# ---------------------------------------------------------------------------
# opencode serve returns all agents including internal ones (compaction, title,
# summary) marked with hidden: true. We filter those out — only user-facing
# agents become A2A skills.
#
# Skill fields:
#   id          — dynamic: "opencode.{agent.id}" from /api/agent
#   name        — dynamic: "OpenCode {agent.id}" titlecased from /api/agent
#   description — dynamic: agent.description from /api/agent
#   tags        — dynamic: ["opencode", "coding", agent.mode] from /api/agent
#   examples    — hardcoded: per-skill prompts (not available from /api/agent)
#   inputModes  — hardcoded: OpenCode accepts text/plain + octet-stream
#   outputModes — hardcoded: OpenCode returns text/plain + application/json
#
# skills[].parameters is not included — OpenCode skills accept free-text
# prompts, not structured parameters. opencode-a2a upstream also omits it.


def _visible_agents(agents: list[dict]) -> list[dict]:
    return [a for a in agents if not a.get("hidden", False)]


def _build_skills(visible: list[dict]) -> list[dict]:
    if not visible:
        return [FALLBACK_SKILL]

    skills = []
    for agent in visible:
        agent_id = agent.get("id", "unknown")
        mode = agent.get("mode", "")
        tags = ["opencode", "coding"]
        if mode:
            tags.append(mode)

        skill: dict = {
            "id": f"opencode.{agent_id}",
            "name": f"OpenCode {agent_id.title()}",
            "description": agent.get("description", ""),
            "tags": tags,
            "inputModes": list(DEFAULT_INPUT_MODES),
            "outputModes": list(DEFAULT_OUTPUT_MODES),
        }

        examples = SKILL_EXAMPLES.get(agent_id)
        if examples:
            skill["examples"] = examples

        skills.append(skill)

    return skills


# ---------------------------------------------------------------------------
# Description — dynamic, enriched from multiple endpoints
# ---------------------------------------------------------------------------
# Base text from env var A2A_DESCRIPTION. Appends agent names from /api/agent,
# provider names from /api/provider, and model count from /api/model.


def _build_description(
    base: str,
    visible: list[dict],
    providers: list[dict],
    models: list[dict],
) -> str:
    parts = [f"{base.rstrip('.')}."]

    agent_names = [a["id"] for a in visible if a.get("id")]
    if agent_names:
        parts.append(f"Available agents: {', '.join(agent_names)}.")

    provider_names = [
        p.get("name", p.get("id", ""))
        for p in providers
        if not p.get("disabled")
    ]
    if provider_names:
        parts.append(f"Connected providers: {', '.join(provider_names)}.")

    enabled_models = [m for m in models if m.get("enabled", True)]
    if enabled_models:
        parts.append(f"{len(enabled_models)} models available.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Card assembly
# ---------------------------------------------------------------------------
# Combines all three sources:
#   Configurable (env vars): name, version, url, provider, docs url, icon
#   Dynamic (opencode serve): skills, description
#   Hardcoded (OpenCode facts): input/output modes, capabilities


async def build_agent_card(settings: Settings, client: OpencodeClient) -> dict:
    agents, providers, models = await asyncio.gather(
        client.fetch_agents(),
        client.fetch_providers(),
        client.fetch_models(),
    )
    visible = _visible_agents(agents)

    card: dict = {
        # Configurable — from env vars
        "name": settings.a2a_title,
        "version": settings.a2a_version,
        "url": settings.public_url,

        # Dynamic — built from opencode serve responses
        "description": _build_description(
            settings.a2a_description, visible, providers, models,
        ),
        "skills": _build_skills(visible),

        # Hardcoded — OpenCode capabilities that don't change per deployment
        "defaultInputModes": list(DEFAULT_INPUT_MODES),
        "defaultOutputModes": list(DEFAULT_OUTPUT_MODES),
        "capabilities": {
            "streaming": False,           # not yet — RHAIENG-5826
            "pushNotifications": False,
            "stateTransitionHistory": False,
            "extensions": [],             # not yet — RHAIENG-5826
        },
    }

    # Configurable — optional fields from env vars, omitted if not set
    if settings.a2a_provider_org or settings.a2a_provider_url:
        provider = {}
        if settings.a2a_provider_org:
            provider["organization"] = settings.a2a_provider_org
        if settings.a2a_provider_url:
            provider["url"] = settings.a2a_provider_url
        card["provider"] = provider

    if settings.a2a_documentation_url:
        card["documentationUrl"] = settings.a2a_documentation_url

    if settings.a2a_icon_url:
        card["iconUrl"] = settings.a2a_icon_url

    return card
