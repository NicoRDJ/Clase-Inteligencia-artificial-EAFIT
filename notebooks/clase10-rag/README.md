# Clase 10 — Prompt engineering y RAG

| Notebook | Qué es | Resultado |
|---|---|---|
| [`00_prompt_engineering_resuelto.ipynb`](00_prompt_engineering_resuelto.ipynb) | 9 ejercicios de prompting con Gemini: tokenización, alucinaciones, instrucciones, personas, few-shot, CoT, formato de salida, Pydantic y pydantic-ai | Cada ejercicio con su celda de solución (las variaciones pedidas) y observaciones. Ejemplo: CoT corrige un problema tipo *bat and ball* (6.40 ❌ → 6.55 ✅) |
| [`03_rag_workshop_papers_resuelto.ipynb`](03_rag_workshop_papers_resuelto.ipynb) | Workshop: RAG sobre *Attention Is All You Need* y *RAG* (MarkItDown → chunks → Qdrant → LCEL) | 214 chunks indexados · quiz 4/5 exactas + 1 superficial · bonus parcial · 0 alucinaciones (con prueba fuera de alcance) · reflexión con umbral calibrado |

**Requisitos:** `requirements.txt` + `GOOGLE_API_KEY` en un `.env` en la raíz del repo (no versionado).

**Nota sobre la cuota gratuita de Gemini:** el free tier permite ~10 peticiones/min y ~20/día por modelo. El workshop indexa por lotes con pausa y usa `InMemoryRateLimiter`. El notebook de prompting espacia las llamadas y, si un modelo agota su cuota diaria, pasa a otro modelo *flash-lite* e imprime cuál respondió.
