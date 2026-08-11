"""
Entrypoint de produção da Yelena V3.

Inicializa o Runtime via Gateway e expõe a HTTP API
para o intermediário Discord + IA existente.

Não contém lógica Discord. Não embute secrets.
"""

from __future__ import annotations

import logging
import os
import sys

logging.basicConfig(
    level=os.getenv("YELENA_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("yelena.main")


def create_application():
    from app.integration.gateway import YelenaGateway
    from app.integration.http_api import create_app

    gateway = YelenaGateway()
    return create_app(gateway)


# ASGI app para uvicorn / Render
app = create_application()


def main() -> int:
    import uvicorn

    host = os.getenv("YELENA_HOST", "0.0.0.0")
    port = int(os.getenv("PORT") or os.getenv("YELENA_PORT") or "8000")

    logger.info("starting Yelena V3", extra={"host": host, "port": port})
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            log_level=os.getenv("YELENA_LOG_LEVEL", "info").lower(),
        )
        return 0
    except Exception:
        logger.exception("failed to start production server")
        return 1


if __name__ == "__main__":
    sys.exit(main())
