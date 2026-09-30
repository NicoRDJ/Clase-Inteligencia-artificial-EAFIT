"""El "oído" de JARVIS: escucha siempre, despierta con "Hey JARVIS", entiende en
cualquier idioma, responde con voz y se deja interrumpir.

    python -m jarvis.voice.ears

Flujo:  micrófono ─► openWakeWord ("hey jarvis") ─► grabar hasta silencio (VAD)
        ─► Whisper (detecta idioma) ─► /ask en el servidor ─► TTS por frases ─► parlante
Mientras habla, sigue escuchando la palabra de activación: decir "Hey JARVIS"
lo interrumpe (barge-in). Cada cambio de estado se publica al HUD.
"""
from __future__ import annotations

import os
import queue
import threading
import time

import numpy as np
import requests
import sounddevice as sd

from jarvis.voice.backends import SR_TTS, make_stt, make_tts, split_sentences

SERVER = os.getenv("JARVIS_SERVER", "http://127.0.0.1:8765")
SR = 16_000
FRAME = 1280                      # 80 ms, lo que espera openWakeWord
WAKE_THRESHOLD = float(os.getenv("JARVIS_WAKE_THRESHOLD", "0.5"))
SILENCE_S, MAX_UTTERANCE_S = 0.9, 15.0
IDIOMAS = {"es": "español", "en": "inglés", "fr": "francés", "it": "italiano", "pt": "portugués",
           "de": "alemán", "ja": "japonés", "zh": "chino"}


def emit(state: str, **kw):
    try:
        requests.post(f"{SERVER}/voice/event", json={"state": state, **kw}, timeout=2)
    except requests.RequestException:
        pass


def chime(freqs=(880, 1320), dur=0.07):
    t = np.linspace(0, dur, int(SR_TTS * dur), endpoint=False)
    tone = np.concatenate([0.18 * np.sin(2 * np.pi * f * t) * np.hanning(len(t)) for f in freqs])
    sd.play(tone.astype(np.float32), SR_TTS)
    sd.wait()


class Ears:
    def __init__(self):
        from openwakeword.model import Model
        print("Cargando palabra de activación, oído y voz…", flush=True)
        self.wake = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx", vad_threshold=0.3)
        self.stt, self.tts = make_stt(), make_tts()
        print(f"  oído: {self.stt.name} · voz: {self.tts.name}", flush=True)
        self.frames: queue.Queue[np.ndarray] = queue.Queue()
        self.speaking = threading.Event()
        self.interrupt = threading.Event()
        self.noise = 0.004

    # ── micrófono (hilo de audio) ──
    def _on_audio(self, indata, frames, t, status):
        self.frames.put(indata[:, 0].copy())

    def _wake_hit(self, frame: np.ndarray) -> bool:
        pcm = (frame * 32767).astype(np.int16)
        score = self.wake.predict(pcm).get("hey_jarvis", 0.0)
        return score >= (WAKE_THRESHOLD + 0.2 if self.speaking.is_set() else WAKE_THRESHOLD)

    def _record(self) -> np.ndarray:
        """Graba hasta ~0.9 s de silencio (umbral adaptativo sobre el ruido de fondo)."""
        buf, silent, started, t0 = [], 0.0, False, time.time()
        while time.time() - t0 < MAX_UTTERANCE_S:
            f = self.frames.get()
            buf.append(f)
            rms = float(np.sqrt(np.mean(f ** 2)))
            if rms > max(self.noise * 3.0, 0.012):
                started, silent = True, 0.0
            else:
                silent += FRAME / SR
                if not started:
                    self.noise = 0.95 * self.noise + 0.05 * rms
            if started and silent >= SILENCE_S:
                break
            if not started and time.time() - t0 > 5:
                break
        return np.concatenate(buf) if buf else np.zeros(1, np.float32)

    # ── habla, con interrupción ──
    def say(self, text: str, lang: str):
        self.speaking.set(); self.interrupt.clear()
        emit("speaking", text=text)
        try:
            for sentence in split_sentences(text):
                if self.interrupt.is_set():
                    break
                audio = self.tts.synth(sentence, lang)
                sd.play(audio.astype(np.float32), SR_TTS)
                while sd.get_stream().active:
                    if self.interrupt.is_set():
                        sd.stop(); break
                    time.sleep(0.03)
        finally:
            self.speaking.clear()
            emit("idle")

    def handle(self):
        chime()
        emit("listening")
        audio = self._record()
        if len(audio) < SR * 0.4:
            emit("idle"); return
        emit("thinking")
        text, lang = self.stt.transcribe(audio, SR)
        if not text:
            emit("idle"); return
        emit("heard", text=text, lang=lang)
        try:
            r = requests.post(f"{SERVER}/ask", json={"text": text, "session": "voz", "fast": True, "lang": lang},
                              timeout=120).json()
            reply = r["text"]
        except requests.RequestException:
            reply = "I've lost connection to my systems, sir." if lang == "en" else "Perdí la conexión con mis sistemas, señor."
        threading.Thread(target=self.say, args=(reply, lang), daemon=True).start()

    def run(self):
        emit("idle")
        with sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=FRAME, callback=self._on_audio):
            print("JARVIS escuchando. Diga «Hey JARVIS».", flush=True)
            while True:
                f = self.frames.get()
                if self._wake_hit(f):
                    self.wake.reset()
                    if self.speaking.is_set():         # barge-in: interrumpir y atender
                        self.interrupt.set()
                        while self.speaking.is_set():
                            time.sleep(0.02)
                    with self.frames.mutex:
                        self.frames.queue.clear()
                    self.handle()


if __name__ == "__main__":
    Ears().run()
