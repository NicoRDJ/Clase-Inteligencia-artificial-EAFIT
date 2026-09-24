# Clase 9 — Transformers y NLP (LLMs, chatbots, RAG)

| Notebook | Tema | Estado |
|---|---|---|
| `05_ejercicio_nvidia_documentos_resuelto.ipynb` | Asistente de documentos con NVIDIA NIM + Gradio sobre *Attention Is All You Need* | 🟡 código completo; **Paso 1 ejecutado de verdad** (extracción del PDF), Pasos 2-4 sin ejecutar (requieren `NVIDIA_API_KEY` propia) |

`01_local_chatbot_lab`, `02_local_remote_hf_chatbot_lab`, `03_nvidia_chatbot_lab`
y `04_nvidia_gradio_lab` no tienen celdas en blanco (son notebooks guiados) —
no se tocaron.

## Ejercicio 05

Las 4 celdas "Escribe tu código aquí" están resueltas:

1. **Extracción del PDF** (`pypdf`) — ejecutada aquí: el paper tiene 15
   páginas y se extraen 39,510 caracteres de texto.
2. **Cliente de NVIDIA NIM** (`openai` apuntando a
   `https://integrate.api.nvidia.com/v1`).
3. **Función de chat con el documento** (`build_system_prompt`,
   `history_to_messages`, `chat_con_documento` con streaming).
4. **Interfaz Gradio** (`gr.ChatInterface` con el texto del documento como
   input oculto).

Los pasos 2-4 no se ejecutaron en este entorno porque requieren una
`NVIDIA_API_KEY` personal (gratuita en
[build.nvidia.com/settings/api-keys](https://build.nvidia.com/settings/api-keys)).
Para probarlos: crear un archivo `.env` en esta carpeta con
`NVIDIA_API_KEY="tu_key"` y correr `Restart & Run All`.
