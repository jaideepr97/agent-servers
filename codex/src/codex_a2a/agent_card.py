from __future__ import annotations

import asyncio

from .config import Settings
from .skill_scanner import CodexSkill, ScanResult, SkillScanner

FALLBACK_SKILL: dict = {
    "id": "codex.chat",
    "name": "Codex Chat",
    "description": "AI coding agent for code generation, editing, review, and debugging",
    "tags": ["codex", "coding", "agent"],
    "examples": [
        "Fix the failing test in auth.py",
        "Refactor this module to use async/await",
        "Explain what this function does",
    ],
}


def _map_skill(skill: CodexSkill) -> dict:
    a2a_skill: dict = {
        "id": f"codex.{skill.name}",
        "name": skill.display_name or skill.name.replace("-", " ").title(),
        "description": skill.short_description or skill.description,
        "tags": _build_tags(skill),
    }
    if skill.default_prompt:
        a2a_skill["examples"] = [skill.default_prompt]
    return a2a_skill


def _build_tags(skill: CodexSkill) -> list[str]:
    tags = ["codex", skill.scope]
    if skill.plugin_name:
        tags.append(skill.plugin_name)
    return tags


def _build_skills(scan: ScanResult) -> list[dict]:
    if not scan.skills:
        return [FALLBACK_SKILL]
    return [_map_skill(s) for s in scan.skills]


def _build_description(base: str, scan: ScanResult) -> str:
    parts = [f"{base.rstrip('.')}."]
    if scan.skills:
        count = len(scan.skills)
        parts.append(f"{count} skill{'s' if count != 1 else ''} discovered.")
    if scan.config.model:
        parts.append(f"Model: {scan.config.model}.")
    if scan.config.mcp_server_count:
        n = scan.config.mcp_server_count
        parts.append(f"{n} MCP server{'s' if n != 1 else ''} configured.")
    if scan.plugin_count:
        n = scan.plugin_count
        parts.append(f"{n} plugin{'s' if n != 1 else ''} installed.")
    return " ".join(parts)


async def build_agent_card(settings: Settings, scanner: SkillScanner) -> dict:
    scan = await asyncio.to_thread(scanner.scan)

    card: dict = {
        "name": settings.a2a_title,
        "description": _build_description(settings.a2a_description, scan),
        "version": settings.a2a_version,
        "supportedInterfaces": [
            {
                "url": settings.public_url,
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": settings.a2a_version,
            },
        ],
        # TODO: Enable when full A2A task execution is implemented via
        # the stdio bridge to codex app-server (SendMessage, streaming, etc.)
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "defaultInputModes": settings.input_modes_list,
        "defaultOutputModes": settings.output_modes_list,
        "skills": _build_skills(scan),
    }

    provider: dict = {}
    if settings.a2a_provider_org:
        provider["organization"] = settings.a2a_provider_org
    if settings.a2a_provider_url:
        provider["url"] = settings.a2a_provider_url
    if provider:
        card["provider"] = provider

    if settings.a2a_documentation_url:
        card["documentationUrl"] = settings.a2a_documentation_url
    if settings.a2a_icon_url:
        card["iconUrl"] = settings.a2a_icon_url

    return card
