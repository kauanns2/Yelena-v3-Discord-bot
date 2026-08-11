"""
Entrypoint de produção da Yelena V3.

Render / qualquer host só executa este arquivo.
Não contém lógica Discord, nem lógica dos 16 módulos.

Fluxo:
  start → Gateway.start() → Runtime.bootstrap()/start() → health
  request → Gateway.process() → Runtime.process()
  shutdown → Gateway.stop() → Runtime.stop()
"""

from __future__ import annotations

import logging
import os
import sys


def _configure_logging() -> None:
    level = os.getenv("YELENA_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


_configure_logging()
logger = logging.getLogger("yelena.main")


def create_application():
    """Cria a app ASGI. A inicialização real do Runtime ocorre no startup."""
    from app.integration.gateway import YelenaGateway
    from app.integration.http_api import create_app

    gateway = YelenaGateway()
    return create_app(gateway)


# App ASGI exposta para uvicorn (Render usa este símbolo via main:app ou python main.py)
app = create_application()


def main() -> int:
    """Comando de start de produção."""
    import uvicorn

    host = os.getenv("YELENA_HOST", "0.0.0.0")
    # Render injeta PORT; fallback local 8000
    port = int(os.getenv("PORT") or os.getenv("YELENA_PORT") or "8000")
    log_level = os.getenv("YELENA_LOG_LEVEL", "info").lower()

    logger.info(
        "starting Yelena V3 entrypoint host=%s port=%s python=%s",
        host,
        port,
        sys.version.split()[0],
    )

    try:
        # O lifecycle do Runtime é ligado em app startup/shutdown (http_api).
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            log_level=log_level,
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
        return 0
    except KeyboardInterrupt:
        logger.info("shutdown requested")
        return 0
    except Exception:
        logger.exception("failed to start production server")
        return 1


if __name__ == "__main__":
    sys.exit(main())
