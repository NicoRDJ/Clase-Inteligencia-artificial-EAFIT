"""Catálogo de cerebros disponibles: solo modelos insignia (los top de cada proveedor).

El modelo exacto se detecta con `python -m jarvis.brains.discover` y queda en .env.

Los precios (USD / 1M tokens) son configurables: verifícalos en la página de
precios de cada proveedor y ajústalos aquí o con variables de entorno. Un
cerebro solo se activa si su llave está en el .env (el local siempre).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .base import Brain, BrainSpec
from .providers import ClaudeBrain, GeminiBrain, OllamaBrain, OpenAICompatibleBrain

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _f(var: str, default: float) -> float:
    return float(os.getenv(var, default))


SPECS: dict[str, BrainSpec] = {
    "local": BrainSpec("local", "ollama", os.getenv("JARVIS_LOCAL_MODEL", "qwen3:4b-instruct-2507-q4_K_M"),
                       0.0, 0.0, local=True),
    "claude": BrainSpec("claude", "anthropic", os.getenv("JARVIS_CLAUDE_MODEL", "claude-opus-5-5"),
                        _f("PRICE_CLAUDE_IN", 5.0), _f("PRICE_CLAUDE_OUT", 25.0)),
    "gpt": BrainSpec("gpt", "openai", os.getenv("JARVIS_GPT_MODEL", "gpt-5"),
                     _f("PRICE_GPT_IN", 1.25), _f("PRICE_GPT_OUT", 10.0)),
    "gemini": BrainSpec("gemini", "google", os.getenv("JARVIS_GEMINI_MODEL", "gemini-3.5-flash"),
                        _f("PRICE_GEMINI_IN", 0.0), _f("PRICE_GEMINI_OUT", 0.0)),   # plan gratuito
    "grok": BrainSpec("grok", "xai", os.getenv("JARVIS_GROK_MODEL", "grok-4"),
                      _f("PRICE_GROK_IN", 3.0), _f("PRICE_GROK_OUT", 15.0)),
}

_KEY_FOR = {"google": "GOOGLE_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY"}
_IMPL = {"ollama": OllamaBrain, "google": GeminiBrain, "anthropic": ClaudeBrain, "openai": OpenAICompatibleBrain, "xai": OpenAICompatibleBrain}


def available() -> list[str]:
    return [n for n, s in SPECS.items() if s.local or os.getenv(_KEY_FOR[s.provider])]


def load(name: str) -> Brain:
    spec = SPECS[name]
    return _IMPL[spec.provider](spec)
