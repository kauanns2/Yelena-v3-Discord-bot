"""HTTP JSON API opcional para o intermediário.

Usada quando o intermediário chama a Yelena via HTTP (ex.: Render).
Não implementa Discord. Não armazena tokens Discord.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.integration.contracts import ProcessMessageRequest
from app.integration.gateway import YelenaGateway
from app.runtime.errors import RuntimeNotStartedError

logger = logging.getLogger(__name__)


def create_app(gateway: YelenaGateway | None = None) -> FastAPI:
    gw = gateway or YelenaGateway()
    app = FastAPI(
        title="Yelena V3 Integration API",
        description="Borda HTTP para o intermediário Discord + IA existente",
        version="3.0.0-dev",
    )

    api_key = os.getenv("YELENA_HTTP_API_KEY", "").strip()

    def _check_auth(x_api_key: str | None) -> None:
        if not api_key:
            return  # auth desabilitada se não configurada
        if not x_api_key or x_api_key != api_key:
            raise HTTPException(status_code=401, detail="unauthorized")

    @app.on_event("startup")
    def _startup() -> None:
        try:
            gw.start()
            logger.info("integration HTTP API startup complete")
        except Exception:
            logger.exception("failed to start YelenaGateway")
            raise

    @app.on_event("shutdown")
    def _shutdown() -> None:
        try:
            gw.stop()
        except Exception:
            logger.exception("error during gateway shutdown")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return gw.health()

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "yelena-v3",
            "status": gw.state,
            "docs": "/docs",
            "health": "/health",
            "process": "POST /v1/process",
        }

    @app.post("/v1/process")
    async def process_message(
        request: Request,
        x_api_key: str | None = Header(default=None),
    ) -> JSONResponse:
        _check_auth(x_api_key)
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="invalid JSON body") from exc

        try:
            req = ProcessMessageRequest.from_dict(body)
            resp = gw.process(req)
            return JSONResponse(resp.to_dict())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except RuntimeNotStartedError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("process failed")
            raise HTTPException(status_code=500, detail="internal error") from exc

    # referência para testes
    app.state.gateway = gw  # type: ignore[attr-defined]
    return app
