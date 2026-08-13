"""Mensagem de voz nativa do Discord — sem anexo solto."""

from __future__ import annotations

import base64
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VOICE_MESSAGE_FLAG = 1 << 13


def _ffmpeg_bin() -> str | None:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def mp3_to_ogg_opus(mp3_path: str | Path) -> tuple[Path, float] | None:
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
            return None
        duration = _estimate_duration(ffmpeg, out)
        return out, duration
    except Exception:
        out.unlink(missing_ok=True)
        logger.exception("mp3_to_ogg_opus failed")
        return None


def _estimate_duration(ffmpeg: str, path: Path) -> float:
    try:
        r = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, timeout=15)
        err = (r.stderr or b"").decode("utf-8", errors="ignore")
        import re

        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", err)
        if m:
            h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mi * 60 + s
    except Exception:
        pass
    return max(1.0, path.stat().st_size / 8000.0)


def fake_waveform(n: int = 256) -> str:
    data = bytes(int(40 + 80 * abs((i % 32) - 16) / 16) for i in range(n))
    return base64.b64encode(data).decode("ascii")


async def send_native_voice_message(
    channel: Any, audio_path: str | Path, *, fallback_text: str = ""
) -> bool:
    """Só mensagem de voz nativa. Nunca envia anexo de arquivo solto."""
    audio_path = Path(audio_path)
    if not audio_path.is_file():
        return False

    ogg_path = audio_path
    duration = 3.0
    converted = None

    if audio_path.suffix.lower() != ".ogg":
        conv = mp3_to_ogg_opus(audio_path)
        if not conv:
            if fallback_text:
                await channel.send(fallback_text[:1900])
            return False
        ogg_path, duration = conv
        converted = ogg_path

    try:
        import discord

        waveform = fake_waveform()

        # 1) flags nativas se a lib suportar
        try:
            if hasattr(discord.MessageFlags, "voice_message") or hasattr(
                discord.MessageFlags(), "voice_message"
            ):
                file = discord.File(str(ogg_path), filename="voice-message.ogg")
                await channel.send(
                    file=file,
                    flags=discord.MessageFlags(voice_message=True),
                )
                return True
        except Exception:
            logger.info("voice_message flag path failed")

        # 2) HTTP com flag IS_VOICE_MESSAGE
        try:
            http = channel._state.http
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
                await http.send_files(
                    channel.id,
                    files=[discord.File(fp, filename="voice-message.ogg")],
                    payload=payload,
                )
            return True
        except Exception:
            logger.exception("HTTP native voice failed")

        # SEM fallback de arquivo — só texto
        if fallback_text:
            await channel.send(fallback_text[:1900])
        else:
            await channel.send(
                "Não consegui mandar voz nativa no chat. "
                "Entra na call e me chama que eu falo aí."
            )
        return False
    finally:
        if converted is not None:
            try:
                converted.unlink(missing_ok=True)
            except Exception:
                pass
