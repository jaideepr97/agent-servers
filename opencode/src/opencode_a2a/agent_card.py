from __future__ import annotations

from .config import Settings
from .opencode_client import OpencodeClient

DEFAULT_INPUT_MODES = ["text/plain", "application/octet-stream"]
DEFAULT_OUTPUT_MODES = ["text/plain", "application/json"]

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

FALLBACK_SKILL = {
    "id": "opencode.chat",
    "name": "OpenCode Chat",
    "description": "AI coding assistant for code generation, editing, and review",
    "tags": ["opencode", "coding", "assistant"],
    "examples": SKILL_EXAMPLES.get("build", []),
    "inputModes": list(DEFAULT_INPUT_MODES),
    "outputModes": list(DEFAULT_OUTPUT_MODES),
}


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


async def build_agent_card(settings: Settings, client: OpencodeClient) -> dict:
    agents, providers, models = (
        await client.fetch_agents(),
        await client.fetch_providers(),
        await client.fetch_models(),
    )
    visible = _visible_agents(agents)

    card: dict = {
        "name": settings.a2a_title,
        "description": _build_description(
            settings.a2a_description, visible, providers, models,
        ),
        "version": settings.a2a_version,
        "url": settings.public_url,
        "skills": _build_skills(visible),
        "defaultInputModes": list(DEFAULT_INPUT_MODES),
        "defaultOutputModes": list(DEFAULT_OUTPUT_MODES),
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False,
            "extensions": [],
        },
    }

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
