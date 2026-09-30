# JARVIS — Referencias y visión de producto

Investigación hecha sobre el JARVIS de las películas (Marvel / Perception, el estudio que diseñó sus interfaces) y sobre los JARVIS reales que la comunidad construyó en 2025–2026. Esto es lo que define "hacerlo bien".

## 1. Lo que hace que JARVIS se sienta JARVIS (películas)

| Rasgo | En las películas | Cómo se traduce aquí |
|---|---|---|
| **Personalidad** | Mayordomo británico, ingenio seco, "señor", nunca servil | `PERSONA` en `assistant.py`; voz masculina sobria (Reed es-ES) |
| **Presencia visual** | Núcleo tipo reactor, anillos giratorios, marcas radiales, paneles de cristal azul-cian, acentos ámbar, líneas de escaneo | HUD en `jarvis/web/`: canvas del reactor que **reacciona al estado** (espera / escucha / procesa / habla) |
| **Arranque** | "Welcome home, sir" + secuencia de sistemas | Pantalla de arranque con checklist de subsistemas y saludo según la hora |
| **Proactividad** | Informa sin que le pregunten (estado, alertas) | Paneles vivos: cerebros, gasto, clima de Medellín, memoria. *(Parte 2: brief matutino)* |
| **Transparencia** | Tony ve qué está haciendo JARVIS | Panel **"Decisión del router"**: qué cerebro respondió, por qué, costo y latencia |

## 2. Lo que aprendí de los JARVIS reales (YouTube, 2025–2026)

| Proyecto | Idea clave | Adopción |
|---|---|---|
| **Naz Louis — "ADA"** | Modelo de audio nativo (Gemini Live): oír-pensar-hablar en un solo modelo → **latencia mínima e interrupciones**; herramientas con **confirmación** antes de acciones peligrosas; memoria por proyectos | Semana 11–13: modo voz en tiempo real con Gemini Live; confirmación obligatoria para acciones irreversibles |
| **Thanh-y Nguyen — LiveKit** | Framework de agentes de voz (open source), visión por cámara, compartir pantalla, app móvil | Semana 13: canal de voz LiveKit + app móvil |
| **Damian Malliaros — Claude Code + Fish Audio** | Voz clonada de alta calidad a bajo costo; brief diario del negocio; integraciones vía Composio | Semana 12: voz neuronal (Fish Audio / Gemini TTS); integraciones Gmail/Calendar |
| **FatihMakes — Mark 55** | Palabra de activación, brief de noticias al iniciar, plugins, globo 3D | Semana 12: wake word "JARVIS" y sistema de plugins |
| **Perception (estudio de VFX)** | La interfaz ficticia funciona porque cada elemento **comunica un estado real** | Regla de diseño: ningún adorno sin dato detrás |

## 3. Requisitos no negociables (los del usuario)

1. **Estético**: HUD a la altura de las películas.
2. **Rápido**: respuesta de texto < 2 s en lo cotidiano (medido: Gemini 3.5 Flash ≈ 1 s), voz sin esperas.
3. **Inteligente**: solo modelos insignia (autodetectados con `jarvis.brains.discover`) + router que elige el mejor por tarea.
4. **Con voz**: entrada y salida por voz (hoy Web Speech; Parte 2 audio nativo).
5. **Autosuficiente**: servicio 24/7 (launchd), se recupera solo, sigue funcionando sin nube gracias al modelo local.
6. **Privado**: los datos sensibles nunca salen del Mac (escudo de privacidad del router).

## 4. Hoja de ruta ligada al curso

| Entrega | Qué demuestra | Estado |
|---|---|---|
| **Checkpoint 1 (sem. 11) — Parte 1** | Router con Naive Bayes + MDP + Q-learning, evaluado contra baselines con métrica cuantitativa | Núcleo listo; faltan datos de cerebros de pago |
| Sem. 9–10 | Red neuronal reemplaza la Q-table; embeddings para intención | Pendiente |
| Sem. 11 | Evaluación sistemática zero/few-shot/CoT de los cerebros (P9) | Pendiente |
| Sem. 12 | RAG sobre archivos personales + voz neuronal | Pendiente |
| Sem. 13 | Agente con herramientas (ReAct) + voz en tiempo real | Pendiente |
| **Checkpoint 2 (sem. 14)** | Seguridad: confirmaciones, permisos, privacidad | Pendiente |
| **Final (sem. 16)** | JARVIS completo en vivo | — |
