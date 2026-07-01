"""
FastAPI application for the OpenCode A2A server.

Routes:
  /.well-known/agent-card.json — A2A agent card (dynamic, cached 30s)
  /.well-known/agent.json      — same card (older A2A spec path)
  /health                      — proxied from opencode serve
  /docs                        — Swagger UI
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .agent_card import build_agent_card
from .config import Settings
from .opencode_client import OpencodeClient

CACHE_TTL_SECONDS = 30


def create_app(settings: Settings) -> FastAPI:
    client = OpencodeClient(settings.opencode_base_url)
    _cache: dict = {"card": None, "expires": 0.0}

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        await client.close()

    app = FastAPI(
        title=settings.a2a_title,
        version=settings.a2a_version,
        lifespan=lifespan,
    )

    # ---------------------------------------------------------------------------
    # A2A discovery — cached to handle frequent polling
    # ---------------------------------------------------------------------------

    @app.get("/.well-known/agent-card.json")
    @app.get("/.well-known/agent.json")
    async def agent_card():
        now = time.monotonic()
        if _cache["card"] and now < _cache["expires"]:
            return JSONResponse(content=_cache["card"])

        card = await build_agent_card(settings, client)
        _cache["card"] = card
        _cache["expires"] = now + CACHE_TTL_SECONDS
        return JSONResponse(content=card)

    # ---------------------------------------------------------------------------
    # Health check — proxied from opencode serve
    # ---------------------------------------------------------------------------

    @app.get("/health")
    async def health():
        result = await client.fetch_health()
        if result:
            return JSONResponse(content=result)
        return JSONResponse(content={"healthy": False}, status_code=503)

    return app
