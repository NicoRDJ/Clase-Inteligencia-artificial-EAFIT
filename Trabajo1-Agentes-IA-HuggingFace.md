# Trabajo 1 — Analizando Agentes de IA con Hugging Face Spaces

**Curso:** Inteligencia Artificial — EAFIT
**Actividad:** Analizando Agentes de IA con Hugging Face Spaces

## Objetivo

Explorar aplicaciones reales de Inteligencia Artificial en Hugging Face Spaces y analizarlas desde la perspectiva de los agentes racionales: identificar sus componentes PEAS, clasificar las propiedades de su entorno, proponer qué tipo de programa de agente podría implementarse detrás del sistema, y justificar cada respuesta.

---

## 1. Nombre del Space

- **Nombre:** Omni Image Editor 2.0
- **Enlace:** https://huggingface.co/spaces/selfit-camera/Omni-Image-Editor

## 2. ¿Qué hace el agente?

Omni Image Editor es una herramienta de edición de imágenes potenciada por IA generativa. El usuario sube una imagen (o escribe únicamente un texto) y el sistema aplica ediciones guiadas por lenguaje natural, genera imágenes desde cero (text-to-image), aumenta la resolución de una imagen existente (upscaling) o elimina marcas de agua, todo desde una interfaz web construida con Gradio.

## 3. Análisis PEAS

| Elemento | Respuesta |
|---|---|
| **Performance** | Que la imagen resultante sea fiel a la instrucción/prompt dado, que preserve las zonas que no debían modificarse, que tenga buena calidad visual (sin artefactos ni distorsiones) y que el tiempo de respuesta sea razonable. |
| **Environment** | El usuario y sus entradas (imagen y/o texto), la infraestructura de cómputo de Hugging Face (CPU/GPU) y el modelo generativo que corre detrás de la interfaz. |
| **Actuators** | Renderizar la imagen editada o generada en pantalla, habilitar la descarga del resultado, mostrar mensajes de estado o progreso. |
| **Sensors** | El campo de carga de imagen, el cuadro de texto donde se escribe el prompt, y los controles/parámetros de la interfaz (por ejemplo, intensidad de edición o resolución objetivo). |

## 4. Clasificación del entorno

| Propiedad | Clasificación | Justificación |
|---|---|---|
| **Observable** | Parcial | El agente solo "ve" el prompt y la imagen cargada; no conoce la intención real ni el contexto completo del usuario detrás de la solicitud. |
| **Determinista** | No | Los modelos generativos (difusión / transformers) usan muestreo estocástico; el mismo input puede producir salidas distintas si no se fija una semilla aleatoria. |
| **Episódico** | Sí | Cada edición o generación se procesa de forma independiente, sin memoria de solicitudes anteriores dentro de la misma sesión. |
| **Estático** | Sí | La imagen de entrada no cambia mientras el modelo procesa la solicitud; no hay eventos externos que alteren el entorno en tiempo real durante el procesamiento. |
| **Discreto** | Discreto (a nivel de interacción) | Las acciones del usuario (subir imagen, escribir prompt, pulsar "generar") son discretas, aunque internamente el modelo opera sobre un espacio continuo de píxeles y parámetros. |
| **Conocido** | Sí, para el usuario | Las reglas de la interfaz (qué hace cada botón o control) son claras y documentadas, aunque el funcionamiento interno del modelo generativo es una "caja negra". |

## 5. ¿Qué tipo de programa de agente creen que es?

**Selección: Agente basado en objetivos.**

El sistema recibe una meta explícita a través del prompt (por ejemplo, "quita el fondo", "genera una imagen de un paisaje al atardecer", "elimina la marca de agua") y debe encontrar, dentro del espacio aprendido por el modelo, una salida que satisfaga esa meta. No aplica un conjunto fijo de reglas condición-acción (por lo cual no es un reflejo simple), ni compara explícitamente la utilidad numérica entre varios resultados posibles antes de elegir uno (por lo cual no encaja estrictamente como "basado en utilidad").

También podría argumentarse que es un **agente basado en modelo**, ya que internamente mantiene una representación latente de la imagen para razonar sobre qué cambios aplicar sin alterar el resto del contenido. Ambas posturas son defendibles y se presentan aquí porque la consigna de la actividad aclara que no existe una única respuesta correcta: lo relevante es justificar la elección a partir del comportamiento observado.

---

## Discusión en clase

**¿Dos Spaces diferentes pueden compartir el mismo tipo de entorno?**
Sí. Dos Spaces con interfaces y propósitos distintos pueden compartir exactamente la misma clasificación de entorno si comparten la estructura de su interacción. Por ejemplo, otro editor de imágenes basado en difusión sería igualmente parcialmente observable, no determinista y episódico, aunque genere resultados visualmente muy diferentes.

**¿Es posible saber con certeza qué tipo de agente implementa un Space únicamente observándolo?**
No con certeza absoluta. Desde afuera solo se puede inferir una hipótesis a partir del comportamiento observado (qué entradas recibe, qué salidas produce, si varía entre ejecuciones idénticas); la arquitectura real, los pesos del modelo y la lógica interna permanecen ocultos, por lo que dos implementaciones muy distintas podrían producir un comportamiento externo indistinguible.

**¿Qué diferencia existe entre el comportamiento observable de un agente y su implementación interna?**
El comportamiento observable es la relación entre las entradas que recibe el agente y las acciones o salidas que produce, tal como la percibe un usuario externo. La implementación interna es el mecanismo concreto (algoritmos, arquitectura de red neuronal, reglas, parámetros) que produce ese comportamiento. Es posible cambiar completamente la implementación interna sin alterar el comportamiento observable, y viceversa: pequeños cambios internos pueden producir comportamientos externos muy distintos.

## Reto adicional

**a) Totalmente observable, determinista y episódico:**
Un Space de clasificación de imágenes simple (por ejemplo, un clasificador de razas de perros basado en ResNet, sin muestreo aleatorio en la salida). Es totalmente observable porque toda la información relevante para la decisión está en la imagen de entrada; es determinista porque la misma imagen siempre produce la misma etiqueta de salida; y es episódico porque cada clasificación es independiente de las anteriores.

**b) Parcialmente observable, estocástico y secuencial:**
Un Space de chat con un modelo de lenguaje (LLM) configurado con temperatura mayor a cero. Es parcialmente observable porque el modelo no conoce el verdadero estado mental o la intención completa del usuario, solo el texto de la conversación; es estocástico porque el muestreo de tokens introduce variabilidad entre respuestas incluso ante el mismo input; y es secuencial porque cada turno de la conversación depende del historial de turnos anteriores, a diferencia de un entorno episódico.

---

## Rúbrica de referencia

| Criterio | Puntos |
|---|---|
| Descripción correcta del Space | 2 |
| Identificación de PEAS | 3 |
| Clasificación del entorno | 3 |
| Justificación del tipo de agente | 2 |
| **Total** | **10** |
