"""Detecta el modelo más potente disponible en cada proveedor y lo fija en .env.

Uso:  python -m jarvis.brains.discover

Regla: se queda con la línea insignia de mayor versión y descarta variantes
económicas (mini, nano, lite, fast, haiku...) y modelos que no son de chat
(audio, imagen, embeddings, tts, realtime...). Así JARVIS usa siempre lo
mejor del mercado sin editar código cuando sale un modelo nuevo.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv, set_key

ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV)

NO_CHAT = re.compile(r"(audio|image|vision|embed|tts|whisper|transcribe|realtime|search|moderation|dall|sora|"
                     r"computer|robotics|codex|instruct|oss|omni|live|native)", re.I)
ECONOMICO = re.compile(r"(mini|nano|lite|fast|haiku|small|flash-8b)", re.I)
FAMILIA_TOP = {  # dentro de Anthropic, orden de capacidad por familia
    "anthropic": ["fable", "opus", "sonnet"],
}


def _version(name: str) -> tuple:
    nums = re.findall(r"\d+(?:\.\d+)?", name.replace("-", "."))
    return tuple(float(n) for n in nums[:3]) or (0,)


def pick(provider: str, names: list[str]) -> str | None:
    cand = [n for n in names if not NO_CHAT.search(n) and not ECONOMICO.search(n)]
    cand = [n for n in cand if not re.search(r"\d{8}$", n) or provider == "anthropic"]
    if provider == "anthropic":
        for fam in FAMILIA_TOP["anthropic"]:
            fam_c = [n for n in cand if fam in n]
            if fam_c:
                return max(fam_c, key=_version)
        return None
    if provider == "openai":
        cand = [n for n in cand if re.match(r"^gpt-\d", n) and "chat" not in n]
    if provider == "xai":
        cand = [n for n in cand if n.startswith("grok-")]
    if provider == "google":
        cand = [n.removeprefix("models/") for n in cand if "gemini" in n and "preview" not in n]
    return max(cand, key=_version) if cand else None


def list_models(provider: str) -> list[str]:
    if provider == "anthropic":
        import anthropic
        return [m.id for m in anthropic.Anthropic().models.list(limit=100)]
    if provider in ("openai", "xai"):
        from openai import OpenAI
        key = os.getenv("OPENAI_API_KEY" if provider == "openai" else "XAI_API_KEY")
        base = None if provider == "openai" else "https://api.x.ai/v1"
        return [m.id for m in OpenAI(api_key=key, base_url=base).models.list()]
    if provider == "google":
        from google import genai
        return [m.name for m in genai.Client(api_key=os.getenv("GOOGLE_API_KEY")).models.list()
                if "generateContent" in (m.supported_actions or [])]
    return []


VARS = {"anthropic": ("ANTHROPIC_API_KEY", "JARVIS_CLAUDE_MODEL"), "openai": ("OPENAI_API_KEY", "JARVIS_GPT_MODEL"),
        "xai": ("XAI_API_KEY", "JARVIS_GROK_MODEL")}


def main():
    for provider, (key_var, model_var) in VARS.items():
        if not os.getenv(key_var):
            print(f"{provider:9s} sin llave → se omite")
            continue
        try:
            best = pick(provider, list_models(provider))
        except Exception as e:
            print(f"{provider:9s} error al listar modelos: {str(e)[:90]}")
            continue
        if best:
            set_key(str(ENV), model_var, best)
            print(f"{provider:9s} → {best}")


if __name__ == "__main__":
    main()
