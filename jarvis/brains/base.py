"""Interfaz común para todos los "cerebros" de JARVIS.

Cada cerebro (Claude, GPT, Grok, modelo local de Ollama) recibe la misma
petición y devuelve un `BrainResponse` con el texto y las tres magnitudes que
el router necesita para decidir: calidad (se mide aparte), costo y latencia.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class BrainResponse:
    brain: str
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0
    error: str | None = None
    meta: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class BrainSpec:
    """Ficha técnica de un cerebro. Los precios son USD por millón de tokens."""

    name: str
    provider: str
    model: str
    price_in: float
    price_out: float
    local: bool = False

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.price_in + output_tokens * self.price_out) / 1_000_000


class Brain(ABC):
    def __init__(self, spec: BrainSpec):
        self.spec = spec

    @property
    def name(self) -> str:
        return self.spec.name

    @abstractmethod
    def _call(self, prompt: str, system: str, max_tokens: int, temperature: float) -> tuple[str, int, int]:
        """Devuelve (texto, tokens_entrada, tokens_salida)."""

    def ask(self, prompt: str, *, system: str = "", max_tokens: int = 600, temperature: float = 0.2) -> BrainResponse:
        t0 = time.perf_counter()
        try:
            text, tin, tout = self._call(prompt, system, max_tokens, temperature)
            return BrainResponse(
                brain=self.name, text=text, input_tokens=tin, output_tokens=tout,
                cost_usd=self.spec.cost(tin, tout), latency_s=time.perf_counter() - t0,
            )
        except Exception as exc:  # un cerebro caído no debe tumbar a JARVIS
            return BrainResponse(brain=self.name, text="", latency_s=time.perf_counter() - t0,
                                 error=f"{type(exc).__name__}: {exc}")
