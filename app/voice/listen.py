"""Escuta o microfone na call → STT → callback de texto."""

from __future__ import annotations

import asyncio
import audioop
import logging
import os
import struct
import tempfile
import time
import wave
from collections import defaultdict
from pathlib import Path
from typing import Any, Awaitable, Callable, Callable as TypingCallable

from app.voice.correct import correct_transcript
from app.voice.stt import stt_available, transcribe_file

logger = logging.getLogger(__name__)

# PCM 48kHz stereo 16-bit típico do Discord
SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2

# silêncio ~1.2s encerra enunciado; mínimo ~0.6s de fala
SILENCE_SECS = float(os.getenv("YELENA_VAD_SILENCE", "1.2"))
MIN_SPEECH_SECS = float(os.getenv("YELENA_VAD_MIN", "0.55"))
MAX_UTTERANCE_SECS = float(os.getenv("YELENA_VAD_MAX", "12"))
RMS_THRESHOLD = int(os.getenv("YELENA_VAD_RMS", "400"))

TextHandler = Callable[[str, Any], Awaitable[None]]  # (text, member)


class UtteranceBuffer:
    def __init__(self) -> None:
        self.pcm = bytearray()
        self.last_voice = 0.0
        self.started = 0.0
        self.speaking = False

    def reset(self) -> None:
        self.pcm.clear()
        self.last_voice = 0.0
        self.started = 0.0
        self.speaking = False


class CallListener:
    """Agrega PCM por usuário e dispara STT após silêncio."""

    def __init__(self, on_text: TextHandler, *, bot_user_id: int | None = None) -> None:
        self._on_text = on_text
        self._bot_user_id = bot_user_id
        self._buffers: dict[int, UtteranceBuffer] = defaultdict(UtteranceBuffer)
        self._busy: set[int] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._enabled = True

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def pause(self) -> None:
        self._enabled = False

    def resume(self) -> None:
        self._enabled = True

    def on_packet(self, user: Any, data: Any) -> None:
        if not self._enabled or user is None:
            return
        uid = getattr(user, "id", None)
        if uid is None:
            return
        if self._bot_user_id is not None and uid == self._bot_user_id:
            return
        if uid in self._busy:
            return

        pcm = getattr(data, "pcm", None)
        if not pcm:
            return

        now = time.monotonic()
        buf = self._buffers[uid]
        try:
            rms = audioop.rms(pcm, SAMPLE_WIDTH)
        except Exception:
            rms = 0

        if rms >= RMS_THRESHOLD:
            if not buf.speaking:
                buf.speaking = True
                buf.started = now
                buf.pcm.clear()
            buf.pcm.extend(pcm)
            buf.last_voice = now
            # corta se fala demais
            if now - buf.started >= MAX_UTTERANCE_SECS:
                self._flush(uid, user, buf)
            return

        if buf.speaking and buf.last_voice and (now - buf.last_voice) >= SILENCE_SECS:
            if (buf.last_voice - buf.started) >= MIN_SPEECH_SECS and len(buf.pcm) > 8000:
                self._flush(uid, user, buf)
            else:
                buf.reset()

    def _flush(self, uid: int, user: Any, buf: UtteranceBuffer) -> None:
        pcm = bytes(buf.pcm)
        buf.reset()
        if not pcm or not stt_available():
            return
        self._busy.add(uid)
        loop = self._loop
        if loop is None:
            try:
                loop = asyncio.get_event_loop()
            except Exception:
                self._busy.discard(uid)
                return

        async def _job() -> None:
            try:
                path = _pcm_to_wav(pcm)
                if path is None:
                    return
                try:
                    raw = await transcribe_file(path, language="pt")
                finally:
                    Path(path).unlink(missing_ok=True)
                if not raw:
                    return
                text = correct_transcript(raw)
                if len(text) < 2:
                    return
                logger.info("call STT user=%s text=%r", uid, text[:120])
                await self._on_text(text, user)
            except Exception:
                logger.exception("call STT job failed")
            finally:
                self._busy.discard(uid)

        try:
            asyncio.run_coroutine_threadsafe(_job(), loop)
        except Exception:
            self._busy.discard(uid)
            logger.exception("schedule STT failed")


def _pcm_to_wav(pcm: bytes) -> Path | None:
    try:
        fd, name = tempfile.mkstemp(prefix="yelena_utt_", suffix=".wav")
        os.close(fd)
        path = Path(name)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm)
        return path
    except Exception:
        logger.exception("pcm_to_wav failed")
        return None
