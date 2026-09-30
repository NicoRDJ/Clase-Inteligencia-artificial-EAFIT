"""Catálogo de cerebros disponibles.

Los precios (USD / 1M tokens) son configurables: verifícalos en la página de
precios de cada proveedor y ajústalos aquí o con variables de entorno. Un
cerebro solo se activa si su llave está en el .env (el local siempre).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from .base import Brain, BrainSpec
from .providers import ClaudeBrain, OllamaBrain, OpenAICompatibleBrain

load_dotenv()


def _f(var: str, default: float) -> float:
    return float(os.getenv(var, default))


SPECS: dict[str, BrainSpec] = {
    "local": BrainSpec("local", "ollama", os.getenv("JARVIS_LOCAL_MODEL", "qwen3:4b-instruct-2507-q4_K_M"),
                       0.0, 0.0, local=True),
    "claude": BrainSpec("claude", "anthropic", os.getenv("JARVIS_CLAUDE_MODEL", "claude-sonnet-5"),
                        _f("PRICE_CLAUDE_IN", 3.0), _f("PRICE_CLAUDE_OUT", 15.0)),
    "gpt": BrainSpec("gpt", "openai", os.getenv("JARVIS_GPT_MODEL", "gpt-5-mini"),
                     _f("PRICE_GPT_IN", 0.25), _f("PRICE_GPT_OUT", 2.0)),
    "grok": BrainSpec("grok", "xai", os.getenv("JARVIS_GROK_MODEL", "grok-4-fast"),
                      _f("PRICE_GROK_IN", 0.2), _f("PRICE_GROK_OUT", 0.5)),
}

_KEY_FOR = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY"}
_IMPL = {"ollama": OllamaBrain, "anthropic": ClaudeBrain, "openai": OpenAICompatibleBrain, "xai": OpenAICompatibleBrain}


def available() -> list[str]:
    return [n for n, s in SPECS.items() if s.local or os.getenv(_KEY_FOR[s.provider])]


def load(name: str) -> Brain:
    spec = SPECS[name]
    return _IMPL[spec.provider](spec)
