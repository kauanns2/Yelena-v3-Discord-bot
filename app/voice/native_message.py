"""Envia áudio como mensagem de voz nativa do Discord (não anexo solto)."""

from __future__ import annotations

import base64
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VOICE_MESSAGE_FLAG = 1 << 13  # IS_VOICE_MESSAGE


def _ffmpeg_bin() -> str | None:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"  # fallback PATH


def mp3_to_ogg_opus(mp3_path: str | Path) -> tuple[Path, float] | None:
    """Converte mp3 → ogg/opus. Retorna (path, duration_secs)."""
    mp3_path = Path(mp3_path)
    if not mp3_path.is_file():
        return None
    ffmpeg = _ffmpeg_bin()
    if not ffmpeg:
        return None

    fd, out_str = tempfile.mkstemp(prefix="yelena_vm_", suffix=".ogg")
    os.close(fd)
    out = Path(out_str)
    try:
        # duração via ffprobe embutido no mesmo binário quando possível
        probe = subprocess.run(
            [
                ffmpeg,
                "-i",
                str(mp3_path),
                "-acodec",
                "libopus",
                "-ac",
                "1",
                "-ar",
                "48000",
                "-b:a",
                "64k",
                "-y",
                str(out),
            ],
            capture_output=True,
            timeout=60,
        )
        if probe.returncode != 0 or not out.is_file() or out.stat().st_size < 64:
            out.unlink(missing_ok=True)
            logger.warning("ffmpeg convert failed: %s", probe.stderr[-400:] if probe.stderr else "")
            return None

        # estima duração pelo bitrate aproximado se probe falhar
        duration = _estimate_duration(ffmpeg, out)
        return out, duration
    except Exception:
        out.unlink(missing_ok=True)
        logger.exception("mp3_to_ogg_opus failed")
        return None


def _estimate_duration(ffmpeg: str, path: Path) -> float:
    try:
        r = subprocess.run(
            [ffmpeg, "-i", str(path)],
            capture_output=True,
            timeout=15,
        )
        # ffmpeg imprime duration no stderr
        err = (r.stderr or b"").decode("utf-8", errors="ignore")
        import re

        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", err)
        if m:
            h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mi * 60 + s
    except Exception:
        pass
    # fallback: tamanho / 8000
    return max(1.0, path.stat().st_size / 8000.0)


def fake_waveform(n: int = 256) -> str:
    """Waveform visual simples (base64 de bytes 0-255)."""
    # curva suave só pra preview
    data = bytes(int(40 + 80 * abs((i % 32) - 16) / 16) for i in range(n))
    return base64.b64encode(data).decode("ascii")


async def send_native_voice_message(channel: Any, audio_path: str | Path, *, fallback_text: str = "") -> bool:
    """Tenta enviar como voice message nativa. True se ok."""
    audio_path = Path(audio_path)
    if not audio_path.is_file():
        return False

    ogg_path = audio_path
    duration = 3.0
    converted = None

    if audio_path.suffix.lower() != ".ogg":
        conv = mp3_to_ogg_opus(audio_path)
        if conv:
            ogg_path, duration = conv
            converted = ogg_path
        else:
            # sem ffmpeg: tenta mandar mp3 mesmo (alguns clientes aceitam menos)
            ogg_path = audio_path
            duration = max(1.0, audio_path.stat().st_size / 6000.0)

    try:
        import discord

        waveform = fake_waveform()
        # API manual: flags + attachment meta
        file = discord.File(str(ogg_path), filename="voice-message.ogg")

        # discord.py estável: send com flags se suportado
        kwargs: dict[str, Any] = {"file": file}
        try:
            flags = discord.MessageFlags()
            if hasattr(flags, "voice_message"):
                # construir flags corretamente
                kwargs["flags"] = discord.MessageFlags(voice_message=True)
            else:
                # fallback HTTP payload via channel._state.http
                pass
        except Exception:
            pass

        # Tentativa 1: flags voice_message (discord.py recente)
        try:
            if "flags" in kwargs:
                await channel.send(**kwargs)
                return True
        except Exception:
            logger.exception("send voice_message flags failed")

        # Tentativa 2: HTTP raw
        try:
            state = channel._state
            http = state.http
            form = discord.utils.MISSING  # type: ignore
            # usa request multipart simples
            payload = {
                "flags": VOICE_MESSAGE_FLAG,
                "attachments": [
                    {
                        "id": "0",
                        "filename": "voice-message.ogg",
                        "duration_secs": float(duration),
                        "waveform": waveform,
                    }
                ],
            }
            with open(ogg_path, "rb") as fp:
                # discord HTTP send_files
                await http.send_files(
                    channel.id,
                    files=[discord.File(fp, filename="voice-message.ogg")],
                    payload=payload,
                )
            return True
        except Exception:
            logger.exception("HTTP voice message failed")

        # Tentativa 3: só arquivo ogg sem texto (parece menos "pasta")
        try:
            await channel.send(file=discord.File(str(ogg_path), filename="voice-message.ogg"))
            return True
        except Exception:
            logger.exception("ogg file send failed")

        if fallback_text:
            await channel.send(fallback_text[:1900])
        return False
    finally:
        if converted is not None:
            try:
                converted.unlink(missing_ok=True)
            except Exception:
                pass
