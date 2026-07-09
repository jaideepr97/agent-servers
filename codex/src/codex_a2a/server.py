import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .agent_card import build_agent_card
from .config import Settings
from .skill_scanner import SkillScanner


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title=settings.a2a_title, version=settings.a2a_version)
    scanner = SkillScanner(settings)
    _cache: dict = {"card": None, "expires": 0.0}

    @app.get("/.well-known/agent-card.json")
    @app.get("/.well-known/agent.json")
    async def agent_card() -> JSONResponse:
        now = time.monotonic()
        if _cache["card"] and now < _cache["expires"]:
            return JSONResponse(content=_cache["card"])

        card = await build_agent_card(settings, scanner)
        _cache["card"] = card
        _cache["expires"] = now + settings.cache_ttl_seconds
        return JSONResponse(content=card)

    @app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse(content={"healthy": True})

    return app
