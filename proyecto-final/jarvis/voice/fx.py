"""Filtro «JARVIS»: el timbre de la IA de la casa en las películas.

No es la voz de nadie: es procesamiento de señal sobre cualquier voz sintética.
- corte de graves bajo 90 Hz y un poco de cuerpo en 180 Hz (voz cercana, de estudio);
- presencia en 3 kHz y aire en 9 kHz (dicción nítida, "digital");
- compresión suave (volumen parejo, como un sistema de sonido de la casa);
- un chorus muy leve (el brillo sintético que delata que es una IA);
- una sala pequeña con muy poca reverberación (la voz "llena" el taller).
Si `pedalboard` no está instalado, devuelve el audio sin cambios.
"""
from __future__ import annotations

import numpy as np


def jarvis_fx(audio: np.ndarray, sr: int, intensidad: float = 1.0) -> np.ndarray:
    try:
        from pedalboard import (Chorus, Compressor, HighpassFilter, Limiter, PeakFilter, Pedalboard, Reverb)
    except ImportError:
        return audio
    k = max(0.0, min(intensidad, 1.5))
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=90),
        PeakFilter(cutoff_frequency_hz=180, gain_db=1.5 * k, q=0.9),
        PeakFilter(cutoff_frequency_hz=3000, gain_db=2.5 * k, q=1.0),
        PeakFilter(cutoff_frequency_hz=9000, gain_db=2.0 * k, q=0.8),
        Compressor(threshold_db=-20, ratio=2.5, attack_ms=5, release_ms=80),
        Chorus(rate_hz=0.6, depth=0.08, centre_delay_ms=6, feedback=0.0, mix=0.10 * k),
        Reverb(room_size=0.16, damping=0.6, wet_level=0.07 * k, dry_level=1.0, width=0.6),
        Limiter(threshold_db=-1.0),
    ])
    x = np.asarray(audio, dtype=np.float32)
    return board(x[None, :], sr)[0]
