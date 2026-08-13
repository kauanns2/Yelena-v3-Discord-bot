"""Speech-to-text multi-provider.

Prioridade:
1. OPENAI_API_KEY → Whisper
2. GROQ_API_KEY → Whisper na Groq (grátis com conta Groq — não é xAI Grok)
3. Google Web Speech → sem chave
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def _groq_key() -> str:
    # GROQ = groq.com (Whisper). GROK costuma ser confusão com xAI.
    return (
        os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("GROK_API_KEY", "").strip()  # alias se o user errou o nome
    )


def stt_available() -> bool:
    return True


def stt_backend_name() -> str:
    if os.getenv("OPENAI_API_KEY", "").strip():
        return "openai"
    if _groq_key():
        return "groq"
    return "google_free"


async def transcribe_file(path: str | Path, *, language: str = "pt") -> str | None:
    path = Path(path)
    if not path.is_file():
        return None

    if os.getenv("OPENAI_API_KEY", "").strip():
        text = await _openai_whisper(path, language=language)
        if text:
            return text

    if _groq_key():
        text = await _groq_whisper(path, language=language)
        if text:
            return text

    return await _google_free(path, language=language)


async def _openai_whisper(path: Path, *, language: str) -> str | None:
    try:
        import json
        import urllib.request

        key = os.getenv("OPENAI_API_KEY", "").strip()
        boundary = "----YelenaSTT"
        data = path.read_bytes()
        body = b""
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="model"\r\n\r\nwhisper-1\r\n'
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

        return await asyncio.to_thread(_do)
    except Exception:
        logger.exception("OpenAI STT failed")
        return None


async def _groq_whisper(path: Path, *, language: str) -> str | None:
    try:
        import json
        import urllib.request

        key = _groq_key()
        boundary = "----YelenaGroq"
        data = path.read_bytes()
        lang = "pt" if language.startswith("pt") else language
        body = b""
        body += f"--{boundary}\r\n".encode()
        body += (
            b'Content-Disposition: form-data; name="model"\r\n\r\n'
            b"whisper-large-v3\r\n"
        )
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="language"\r\n\r\n'
        body += f"{lang}\r\n".encode()
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        ).encode()
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += data + b"\r\n"
        body += f"--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/audio/transcriptions",
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

        return await asyncio.to_thread(_do)
    except Exception:
        logger.exception("Groq STT failed")
        return None


def _ffmpeg() -> str | None:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _to_16k_mono_wav(src: Path) -> Path | None:
    ffmpeg = _ffmpeg()
    if not ffmpeg:
        return src if src.suffix.lower() == ".wav" else None
    fd, out_str = tempfile.mkstemp(prefix="yelena_stt_", suffix=".wav")
    os.close(fd)
    out = Path(out_str)
    try:
        r = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(src),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                str(out),
            ],
            capture_output=True,
            timeout=30,
        )
        if r.returncode != 0 or not out.is_file() or out.stat().st_size < 64:
            out.unlink(missing_ok=True)
            return None
        return out
    except Exception:
        out.unlink(missing_ok=True)
        logger.exception("ffmpeg convert for STT failed")
        return None


async def _google_free(path: Path, *, language: str) -> str | None:
    def _do() -> str | None:
        try:
            import speech_recognition as sr
        except ImportError:
            logger.error("SpeechRecognition not installed")
            return None

        wav = _to_16k_mono_wav(path)
        if wav is None:
            return None
        cleanup = wav != path
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(str(wav)) as source:
                audio = recognizer.record(source)
            lang = "pt-BR" if language.startswith("pt") else language
            text = recognizer.recognize_google(audio, language=lang)
            return (text or "").strip() or None
        except Exception as exc:
            logger.warning("Google STT failed: %s", exc)
            return None
        finally:
            if cleanup:
                try:
                    wav.unlink(missing_ok=True)
                except Exception:
                    pass

    return await asyncio.to_thread(_do)
