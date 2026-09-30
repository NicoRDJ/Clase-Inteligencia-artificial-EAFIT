"""Implementaciones concretas de cada proveedor."""
from __future__ import annotations

import os

import requests

from .base import Brain, BrainSpec

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


class OllamaBrain(Brain):
    """Modelo local: gratis y privado (los datos nunca salen del Mac)."""

    def _call(self, prompt, system, max_tokens, temperature):
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        r = requests.post(f"{OLLAMA_URL}/api/chat", timeout=600, json={
            "model": self.spec.model, "messages": messages, "stream": False, "think": False,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        })
        r.raise_for_status()
        d = r.json()
        return d["message"]["content"], d.get("prompt_eval_count", 0), d.get("eval_count", 0)


class ClaudeBrain(Brain):
    def __init__(self, spec: BrainSpec):
        super().__init__(spec)
        import anthropic
        self._client = anthropic.Anthropic()

    def _call(self, prompt, system, max_tokens, temperature):
        kwargs = {"system": system} if system else {}
        msg = self._client.messages.create(
            model=self.spec.model, max_tokens=max_tokens,   # la SDK 1.x ya no acepta temperature
            messages=[{"role": "user", "content": prompt}], **kwargs,
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return text, msg.usage.input_tokens, msg.usage.output_tokens


class OpenAICompatibleBrain(Brain):
    """GPT (OpenAI) y Grok (xAI, que expone una API compatible con OpenAI)."""

    BASE_URLS = {"openai": None, "xai": "https://api.x.ai/v1"}
    KEY_VARS = {"openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY"}

    def __init__(self, spec: BrainSpec):
        super().__init__(spec)
        from openai import OpenAI
        self._client = OpenAI(api_key=os.getenv(self.KEY_VARS[spec.provider]), base_url=self.BASE_URLS[spec.provider])

    def _call(self, prompt, system, max_tokens, temperature):
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        resp = self._client.chat.completions.create(
            model=self.spec.model, messages=messages, max_completion_tokens=max_tokens, temperature=temperature,
        )
        u = resp.usage
        return resp.choices[0].message.content or "", u.prompt_tokens, u.completion_tokens


class GeminiBrain(Brain):
    """Gemini: usa el modelo configurado y, si agota cuota o está saturado, rota entre los Flash más nuevos."""

    FALLBACK = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]

    def __init__(self, spec: BrainSpec):
        super().__init__(spec)
        from google import genai
        self._genai = genai
        self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self._agotados: set[str] = set()

    def _call(self, prompt, system, max_tokens, temperature):
        from google.genai import errors, types
        modelos = [self.spec.model] + [m for m in self.FALLBACK if m != self.spec.model]
        ultimo = None
        for modelo in [m for m in modelos if m not in self._agotados]:
            try:
                r = self._client.models.generate_content(
                    model=modelo, contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=system or None,
                                                       max_output_tokens=max_tokens, temperature=temperature))
                u = r.usage_metadata
                return r.text or "", u.prompt_token_count or 0, u.candidates_token_count or 0
            except errors.ClientError as e:
                ultimo = e
                if e.code == 429:
                    self._agotados.add(modelo)
                    continue
                raise
            except errors.ServerError as e:
                ultimo = e
                continue
        raise RuntimeError(f"Gemini sin cuota disponible: {ultimo}")
