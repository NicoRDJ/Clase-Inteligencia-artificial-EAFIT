"""Backends de voz intercambiables (oído y habla) con detección automática de plataforma.

Diseñado para escalar: el mismo JARVIS corre en un Mac con Apple Silicon, en un
PC Windows/Linux con GPU NVIDIA, en un servidor solo-CPU o delegando a la nube.
Cada backend se puede forzar con variables de entorno:

    JARVIS_STT = mlx | faster | openai
    JARVIS_TTS = kokoro | elevenlabs | openai | system

Orden automático (del más rápido/privado al más universal):
    STT: mlx-whisper (Apple Silicon) → faster-whisper (CUDA o CPU, cualquier SO) → OpenAI Whisper API
    TTS: Kokoro (local, 82M, cualquier SO) → ElevenLabs / OpenAI TTS (nube) → voz del sistema operativo
"""
from __future__ import annotations

import os
import platform
import re
import subprocess
import tempfile

import numpy as np

SR_TTS = 24_000

# Voz de JARVIS por idioma (Kokoro). Inglés: británica masculina, el registro del personaje.
KOKORO_VOICES = {
    "en": ("b", "bm_george"), "es": ("e", "em_alex"), "fr": ("f", "ff_siwis"), "it": ("i", "im_nicola"),
    "pt": ("p", "pm_alex"), "ja": ("j", "jm_kumo"), "zh": ("z", "zm_yunjian"), "hi": ("h", "hm_omega"),
}


def is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().total / 2**30
    except Exception:
        return 8.0


def has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


# ───────────────────────────── STT ─────────────────────────────
LANGS = [l.strip() for l in os.getenv("JARVIS_LANGS", "es,en").split(",")]   # idiomas habilitados
WAKE_RE = re.compile(r"^\W*(hey|hei|ey|oye|hola|ok)?\W*(jarvis|jarvi[es]?|yarvis|j'ai revi|charvis|harvis|jervis)\W*",
                     re.IGNORECASE)


def clean_wake(text: str) -> str:
    """Quita el «Hey JARVIS» que Whisper a veces transcribe al inicio."""
    return WAKE_RE.sub("", text).strip()


class STT:
    name = "base"

    def _raw(self, audio: np.ndarray, sr: int, language: str | None) -> tuple[str, str]:
        raise NotImplementedError

    def transcribe(self, audio: np.ndarray, sr: int = 16_000) -> tuple[str, str]:
        """→ (texto, idioma). Si Whisper detecta un idioma no habilitado, se retranscribe
        forzando el habilitado más probable (evita confundir «Jarvis» con francés)."""
        text, lang = self._raw(audio, sr, None)
        if lang not in LANGS:
            forced = "en" if "en" in LANGS and sum(c.isascii() for c in text) > 0.97 * max(len(text), 1) and not re.search(
                r"[áéíóúñ¿¡]", text) and re.search(r"\b(the|what|is|how|you|please|can)\b", text, re.I) else LANGS[0]
            text, lang = self._raw(audio, sr, forced)
            lang = forced
        return clean_wake(text), lang


class MLXWhisperSTT(STT):
    name = "mlx-whisper"

    def __init__(self, model: str | None = None):
        import mlx_whisper
        self._w = mlx_whisper
        # escala con el hardware: equipos con poca RAM usan un modelo pequeño y rápido
        default = "mlx-community/whisper-large-v3-turbo" if ram_gb() >= 16 else "mlx-community/whisper-small-mlx"
        self.model = model or os.getenv("JARVIS_WHISPER_MLX", default)

    def _raw(self, audio, sr, language):
        r = self._w.transcribe(audio.astype(np.float32), path_or_hf_repo=self.model, fp16=True,
                               condition_on_previous_text=False, language=language)
        return r.get("text", "").strip(), r.get("language", language or "es")


class FasterWhisperSTT(STT):
    name = "faster-whisper"

    def __init__(self, model: str | None = None):
        from faster_whisper import WhisperModel
        cuda = has_cuda()
        self._m = WhisperModel(model or os.getenv("JARVIS_WHISPER", "large-v3-turbo" if cuda else "small"),
                               device="cuda" if cuda else "cpu", compute_type="float16" if cuda else "int8")

    def _raw(self, audio, sr, language):
        segs, info = self._m.transcribe(audio.astype(np.float32), vad_filter=True, language=language)
        return " ".join(s.text for s in segs).strip(), info.language


class OpenAIWhisperSTT(STT):
    name = "openai-whisper"

    def _raw(self, audio, sr, language):
        import soundfile as sf
        from openai import OpenAI
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            sf.write(f.name, audio, sr)
            r = OpenAI().audio.transcriptions.create(model="whisper-1", file=open(f.name, "rb"),
                                                      response_format="verbose_json", **({"language": language} if language else {}))
        return r.text.strip(), (getattr(r, "language", "") or "es")[:2]


def make_stt() -> STT:
    forced = os.getenv("JARVIS_STT")
    order = [forced] if forced else (["mlx", "faster", "openai"] if is_apple_silicon() else ["faster", "openai"])
    for name in order:
        try:
            return {"mlx": MLXWhisperSTT, "faster": FasterWhisperSTT, "openai": OpenAIWhisperSTT}[name]()
        except Exception:
            continue
    raise RuntimeError("No hay backend de reconocimiento de voz disponible")


# ───────────────────────────── TTS ─────────────────────────────
def split_sentences(text: str) -> list[str]:
    """Frases cortas → el primer audio sale rápido (streaming por frase)."""
    text = re.sub(r"[*_#`>|]", "", text)
    parts = re.split(r"(?<=[.!?¡¿…;:])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


class TTS:
    name = "base"

    def synth(self, sentence: str, lang: str) -> np.ndarray:
        raise NotImplementedError


class KokoroTTS(TTS):
    name = "kokoro"

    def __init__(self):
        from kokoro import KPipeline
        self._KPipeline = KPipeline
        self._pipes: dict[str, object] = {}
        self._pipe("en")   # precarga la voz principal

    def _pipe(self, lang):
        code = KOKORO_VOICES.get(lang, KOKORO_VOICES["en"])[0]
        if code not in self._pipes:
            self._pipes[code] = self._KPipeline(lang_code=code, repo_id="hexgrad/Kokoro-82M")
        return self._pipes[code]

    def synth(self, sentence, lang):
        voice = os.getenv(f"JARVIS_VOICE_{lang.upper()}") or KOKORO_VOICES.get(lang, KOKORO_VOICES["en"])[1]
        chunks = [r.audio for r in self._pipe(lang)(sentence, voice=voice, speed=1.02)]
        return np.concatenate([np.asarray(c) for c in chunks]) if chunks else np.zeros(1, np.float32)


class ElevenLabsTTS(TTS):
    """Voz premium en la nube. Pensada para una voz propia o con licencia (p. ej. tu voz clonada con consentimiento)."""
    name = "elevenlabs"

    def __init__(self):
        self.key, self.voice = os.environ["ELEVENLABS_API_KEY"], os.environ["ELEVENLABS_VOICE_ID"]

    def synth(self, sentence, lang):
        import requests
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice}?output_format=pcm_24000",
                          headers={"xi-api-key": self.key}, timeout=30,
                          json={"text": sentence, "model_id": "eleven_multilingual_v2"})
        r.raise_for_status()
        return np.frombuffer(r.content, dtype=np.int16).astype(np.float32) / 32768


class OpenAITTS(TTS):
    name = "openai-tts"

    def synth(self, sentence, lang):
        from openai import OpenAI
        pcm = OpenAI().audio.speech.create(model="gpt-4o-mini-tts", voice=os.getenv("JARVIS_OPENAI_VOICE", "onyx"),
                                           input=sentence, response_format="pcm").content
        return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768


class SystemTTS(TTS):
    """Último recurso: la voz del sistema operativo (macOS `say`, Windows SAPI, Linux espeak)."""
    name = "system"

    def synth(self, sentence, lang):
        import soundfile as sf
        with tempfile.NamedTemporaryFile(suffix=".aiff" if platform.system() == "Darwin" else ".wav") as f:
            if platform.system() == "Darwin":
                subprocess.run(["say", "-o", f.name, sentence], check=True)
            else:
                subprocess.run(["espeak-ng", "-v", lang, "-w", f.name, sentence], check=True)
            a, sr = sf.read(f.name, dtype="float32")
        return a if sr == SR_TTS else np.interp(np.linspace(0, len(a), int(len(a) * SR_TTS / sr)), np.arange(len(a)), a)


def make_tts() -> TTS:
    forced = os.getenv("JARVIS_TTS")
    order = [forced] if forced else ["kokoro", "elevenlabs", "openai", "system"]
    for name in order:
        try:
            return {"kokoro": KokoroTTS, "elevenlabs": ElevenLabsTTS, "openai": OpenAITTS, "system": SystemTTS}[name]()
        except Exception:
            continue
    return SystemTTS()
