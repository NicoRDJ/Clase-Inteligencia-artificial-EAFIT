"""Audición de voces para JARVIS: genera el mismo texto con varias voces, en crudo y
con el filtro «JARVIS» (el timbre procesado de la IA de la casa en las películas).

    python -m jarvis.voice.audicion        → data/voices/audiciones/*.wav

Solo voces sintéticas con licencia abierta (Kokoro, Piper). No se clonan voces de
personas reales sin su consentimiento.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from jarvis.voice.fx import jarvis_fx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "voices" / "audiciones"
PIPER = ROOT / "data" / "voices" / "piper"
SR = 24_000

TEXTO = {
    "en": "Good evening, sir. All systems are online. I have taken the liberty of running the diagnostics; "
          "the council agrees the numbers are sound. Shall I prepare the suit?",
    "es": "Buenas noches, señor. Todos los sistemas están en línea. Me he tomado la libertad de ejecutar el diagnóstico; "
          "el consejo coincide en que los números son correctos. ¿Preparo el traje?",
}


def kokoro(lang_code: str, voice, text: str, speed: float = 0.95) -> np.ndarray:
    from kokoro import KPipeline
    pipe = kokoro.pipes.setdefault(lang_code, KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M"))
    if isinstance(voice, dict):     # mezcla de voces: promedio ponderado de los embeddings de estilo
        voice = sum(w * pipe.load_voice(v) for v, w in voice.items())
    return np.concatenate([np.asarray(r.audio) for r in pipe(text, voice=voice, speed=speed)])


kokoro.pipes = {}


def piper(model: str, text: str, length_scale: float = 1.05) -> np.ndarray:
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    v = PiperVoice.load(str(PIPER / f"{model}.onnx"))
    audio = np.concatenate([c.audio_float_array for c in v.synthesize(text, SynthesisConfig(length_scale=length_scale))])
    sr = v.config.sample_rate
    return np.interp(np.linspace(0, len(audio), int(len(audio) * SR / sr), endpoint=False), np.arange(len(audio)), audio)


CANDIDATAS = {
    "en": {
        "kokoro_george": lambda t: kokoro("b", "bm_george", t),
        "kokoro_lewis": lambda t: kokoro("b", "bm_lewis", t),
        "kokoro_daniel": lambda t: kokoro("b", "bm_daniel", t),
        "kokoro_fable": lambda t: kokoro("b", "bm_fable", t),
        "kokoro_george+lewis": lambda t: kokoro("b", {"bm_george": 0.6, "bm_lewis": 0.4}, t),
        "piper_alan": lambda t: piper("en_GB-alan-medium", t),
    },
    "es": {
        "kokoro_alex": lambda t: kokoro("e", "em_alex", t),
        "kokoro_santa": lambda t: kokoro("e", "em_santa", t),
        "piper_mx_ald": lambda t: piper("es_MX-ald-medium", t),
        "piper_mx_claude": lambda t: piper("es_MX-claude-high", t),
        "piper_es_davefx": lambda t: piper("es_ES-davefx-medium", t),
    },
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang, voces in CANDIDATAS.items():
        for nombre, f in voces.items():
            try:
                a = f(TEXTO[lang]).astype(np.float32)
            except Exception as e:
                print(f"  {lang} {nombre}: falló ({e})")
                continue
            sf.write(OUT / f"{lang}_{nombre}_crudo.wav", a, SR)
            sf.write(OUT / f"{lang}_{nombre}_jarvis.wav", jarvis_fx(a, SR), SR)
            print(f"  {lang} {nombre}: {len(a) / SR:.1f} s")


if __name__ == "__main__":
    main()
