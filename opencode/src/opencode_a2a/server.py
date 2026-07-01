from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .agent_card import build_agent_card
from .config import Settings
from .opencode_client import OpencodeClient


def create_app(settings: Settings) -> FastAPI:
    client = OpencodeClient(settings.opencode_base_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        await client.close()

    app = FastAPI(
        title=settings.a2a_title,
        version=settings.a2a_version,
        lifespan=lifespan,
    )

    @app.get("/.well-known/agent-card.json")
    @app.get("/.well-known/agent.json")
    async def agent_card():
        card = await build_agent_card(settings, client)
        return JSONResponse(content=card)

    @app.get("/health")
    async def health():
        result = await client.fetch_health()
        if result:
            return JSONResponse(content=result)
        return JSONResponse(content={"healthy": False}, status_code=503)

    return app
