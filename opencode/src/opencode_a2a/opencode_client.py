"""
HTTP client for querying opencode serve.

Fetches agents, providers, and models to build the agent card dynamically.
All methods return empty lists or None on failure — the card builder
handles fallbacks.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = 5.0


class OpencodeClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=TIMEOUT,
        )

    async def close(self) -> None:
        await self._client.aclose()

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    async def _get(self, path: str) -> Any | None:
        try:
            resp = await self._client.get(path)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.debug("Failed to fetch %s%s", self._base_url, path)
            return None

    async def _get_data(self, path: str) -> list[dict]:
        """OpenCode wraps list responses in {"data": [...]}."""
        result = await self._get(path)
        if isinstance(result, dict):
            return result.get("data", [])
        return []

    # ---------------------------------------------------------------------------
    # Public API — used by agent_card.py
    # ---------------------------------------------------------------------------

    async def fetch_agents(self) -> list[dict]:
        return await self._get_data("/api/agent")

    async def fetch_providers(self) -> list[dict]:
        return await self._get_data("/api/provider")

    async def fetch_models(self) -> list[dict]:
        return await self._get_data("/api/model")

    async def fetch_health(self) -> dict | None:
        result = await self._get("/api/health")
        if isinstance(result, dict):
            return result
        return None
