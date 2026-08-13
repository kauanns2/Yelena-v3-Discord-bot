"""Speech-to-text (opcional).

Prioridade:
1. OPENAI_API_KEY → Whisper API
2. sem chave → None (só texto / call outbound)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def stt_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


async def transcribe_file(path: str | Path, *, language: str = "pt") -> str | None:
    path = Path(path)
    if not path.is_file():
        return None
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        logger.info("STT skipped: OPENAI_API_KEY not set")
        return None
    try:
        import urllib.request
        import json
        # usa API HTTP simples sem dependência openai obrigatória
        boundary = "----YelenaSTT"
        data = path.read_bytes()
        body = b""
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="model"\r\n\r\n'
        body += b"whisper-1\r\n"
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="language"\r\n\r\n'
        body += f"{language}\r\n".encode()
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        ).encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += data + b"\r\n"
        body += f"--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/audio/transcriptions",
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )

        def _do() -> str | None:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return (payload.get("text") or "").strip() or None

        import asyncio

        return await asyncio.to_thread(_do)
    except Exception:
        logger.exception("STT failed")
        return None
