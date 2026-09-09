# Taller a mano — Módulo 1 (búsqueda · optimización · Q-learning)

Resolución paso a paso del taller `workshops/module1/taller_busqueda_optimizacion_q_learning.md`
del repo del curso. Es el taller de preparación que nombra la guía del Examen 01.
Todo el procedimiento está mostrado (las respuestas sin procedimiento no reciben crédito total).

---

## Parte 1 · Algoritmos de búsqueda

Grafo dirigido, costos sobre las aristas. Sucesores de izquierda a derecha. Inicio `S`, meta `G`.

```
S --2--> A        A --2--> C        B --2--> D        C --2--> G
S --1--> B        A --5--> G        B --4--> G        D --1--> G

Sucesores:  S:[A,B]   A:[C,G]   B:[D,G]   C:[G]   D:[G]

Caminos y costo:   S-A-C-G = 6     S-B-D-G = 4 (óptimo)
                   S-A-G   = 7     S-B-G   = 5
```

### 1) Frontera después de expandir S (genera A y B)

| Algoritmo | Estructura | Frontera |
|---|---|---|
| **BFS** | cola FIFO | `[A, B]` (A entró primero) |
| **DFS** | pila LIFO | `[A, B]` con **A en el tope** (se apila B, luego A) |
| **UCS** | cola de prioridad por `g(n)` | `{ B:1 , A:2 }` |

### 2) Siguiente nodo que se expande

- **BFS → A** (primero en la cola)
- **DFS → A** (tope de la pila, rama más a la izquierda)
- **UCS → B** (menor costo acumulado: `g(B)=1 < g(A)=2`)

### 3) Expansión de UCS hasta seleccionar la meta

Prioridad = `g(n)`. La prueba de meta se hace **al extraer**, no al generar.

| Iter. | Nodo sel. | `g(n)` | Frontera después de expandir |
|---:|:---:|---:|---|
| 1 | S | 0 | `{ B:1 , A:2 }` |
| 2 | B | 1 | `{ A:2 , D:3 , G:5 }`  (D vía S-B-D=1+2 ; G vía S-B-G=1+4) |
| 3 | A | 2 | `{ D:3 , C:4 , G:5 , G:7 }`  (C vía S-A-C=2+2 ; G vía S-A-G=2+5) |
| 4 | D | 3 | `{ C:4 , G:4 , G:5 , G:7 }`  (nuevo G:4 vía S-B-D-G=3+1) |

Siguiente extracción: **G con `g=4`** → prueba de meta exitosa.
**Solución: `S → B → D → G`, costo total 4.**
(Empate C:4 / G:4: si sale C primero, expande C→G con g=6, que no mejora el G:4; la siguiente extracción sigue siendo G con g=4. No cambia el resultado.)

### 4) Preguntas

**a)** UCS ordena por costo acumulado `g(n)`, no por profundidad. `g(B)=1 < g(A)=2`, así que B sale primero. (BFS, que ordena por profundidad y generó A primero, expandiría A antes.)

**b)** `S → B → D → G`, costo 4 (el de menor costo de todos).

**c)** No. El primer `G` en la frontera es vía `S-B-G` con `g=5` (iteración 2), pero UCS no acepta la meta al generarla sino al extraerla con el menor `g`. Luego aparece `G` con `g=4` (vía D) y ese se extrae primero. UCS es óptimo precisamente porque **pospone la prueba de meta hasta la extracción**: garantiza que ningún otro camino a G cuesta menos que el que saca.

**d)** Serían equivalentes: con costos unitarios `g(n) = profundidad(n)`, así que ordenar por `g` es ordenar por profundidad. UCS expande por niveles igual que BFS y devuelve el mismo camino (menos aristas). BFS es el caso particular de UCS con costos unitarios.

---

## Parte 2 · Optimización: Simulated Annealing

```
f(s_actual)=8   f(s_nuevo)=11   T=4   r=0.35
Minimización:  Δ = f(s_nuevo) − f(s_actual)
Vecino peor (Δ>0):  P(aceptar) = e^(−Δ/T)
Vecino mejor o igual (Δ≤0):  se acepta siempre
```

1. **Δ = 11 − 8 = 3.**
2. **Δ = +3 > 0 → el nuevo estado es PEOR** (mayor costo en minimización). Si Δ ≤ 0 sería mejor/igual y se aceptaría sin calcular nada.
3. `P(aceptar) = e^(−3/4) = e^(−0.75)`. Como `e^0.75 ≈ 2.117`, **`P ≈ 1/2.117 ≈ 0.47`**.
4. `r = 0.35 < 0.47` → **SÍ se acepta** el movimiento al estado peor.
5. Sin recalcular todo:
   - **T = 0.5:** `−Δ/T = −6`, `P = e^(−6) ≈ 0.0025` → probabilidad casi nula, se rechazaría. A baja temperatura casi no acepta empeoramientos (≈ hill climbing).
   - **T = 20:** `−Δ/T = −0.15`, `P = e^(−0.15) ≈ 0.861` → se aceptaría casi siempre. A alta temperatura explora mucho (casi aleatorio).
6. Conceptual:
   - **a)** Puede aceptar una solución peor para **escapar de óptimos locales**: si solo aceptara mejoras (hill climbing), se quedaría atrapado en el primer valle.
   - **b)** Hill climbing es codicioso y determinista, se estanca en óptimos locales, mesetas y crestas. SA tiene probabilidad no nula de moverse cuesta arriba → **exploración global**, sobre todo al inicio (T alta). Con enfriamiento adecuado converge (en teoría) al óptimo global.
   - **c)** Cuando `T → 0`, `e^(−Δ/T) → 0` para todo `Δ > 0`: la exploración desaparece, el algoritmo solo acepta mejoras (hill climbing puro) y "congela" la solución.
   - **d)** Vecino con costo 5: `Δ = 5 − 8 = −3 < 0` → **es mejor**. No hace falta calcular ninguna probabilidad: los movimientos que mejoran se aceptan siempre.

---

## Parte 3 · Q-learning  *(núcleo del Examen 01)*

```
Acción     Resultado     r      Q(S,a)
Avanzar    llega a S'    +1      2.0
Esperar    sigue en S    −1      0.5
Saltar     cae y muere   −10    −2.0

max_a' Q(S',a') = 4      α = 0.5      γ = 0.9
Q(S,a) ← Q(S,a) + α [ r + γ·max_a' Q(S',a') − Q(S,a) ]
```

El agente selecciona **Avanzar**.

1. **Identificar:** `Q(S,Avanzar) = 2.0` · `r = +1` · `max_a' Q(S',a') = 4`.
2. **TD target** `= r + γ·max_a' Q(S',a') = 1 + 0.9·(4) = 1 + 3.6 =` **`4.6`**.
3. **TD error** `δ = 4.6 − 2.0 =` **`2.6`**.
4. **Actualización:** `Q(S,Avanzar) ← 2.0 + 0.5·(2.6) = 2.0 + 1.3 =` **`3.3`**.
5. **Aumentó** (2.0 → 3.3) porque `δ > 0`: el objetivo temporal (4.6) resultó mayor que la estimación previa (2.0). La experiencia — recompensa +1 y llegar a un `S'` que vale 4 — fue mejor de lo esperado.

### Preguntas de análisis

6. **Q(S,Saltar)** debería ser el valor **más bajo** (mucho más negativo): Saltar da `r = −10` y termina el episodio sin futuro, así que su Q converge hacia −10. Orden: `Q(Saltar) ≪ Q(Esperar) < Q(Avanzar)`.
7. **No.** Si `S'` es terminal, `max_a' Q(S',a') = 0` por convención y `target = r = −10`. La actualización sería `Q(S,Saltar) ← Q(S,Saltar) + α[−10 − Q(S,Saltar)]`.
8. Porque el valor verdadero de Saltar es **−10** (recompensa inmediata, sin futuro). −2 está muy por encima de −10: el agente aún **subestima** lo malo que es saltar. Con más actualizaciones (target = −10) bajará hacia −10.
9. **Avanzar** (mayor `Q(S,a) = 2.0` frente a 0.5 y −2.0). `π_greedy(S) = argmax_a Q(S,a) = Avanzar`.
10. **No.** Con `ε-greedy`, con probabilidad `ε` elige una acción **aleatoria** (podría ser Esperar o Saltar); solo con `1−ε` elige la voraz. Sin exploración nunca actualizaría `Q(S,Esperar)` ni `Q(S,Saltar)` y no podría corregir estimaciones erróneas.
11. **Sí.** `Q(s,a) ≈ r + γ·max_a' Q(s',a')`. Aunque `r = 0`, si `max_a' Q(s',a')` es grande, `γ·max_a' Q(s',a')` hace el target alto y `Q(s,Avanzar)` crece. Q-learning **propaga hacia atrás** (bootstrapping) el valor de las recompensas futuras. Ej.: `γ=0.9`, `max_a' Q(s',a')=10` → `target = 0.9·10 = 9`.
12.

| Parám. | ¿Qué controla? | ¿Qué pasa si es muy alto? |
|---|---|---|
| `α` | Cuánto pesa cada nueva experiencia; tamaño del paso hacia el TD target. | Actualizaciones inestables/oscilantes; el agente "olvida" lo aprendido; puede no converger. `α=1` reemplaza Q por el target. |
| `γ` | Cuánto valora el futuro frente a lo inmediato; horizonte de planeación. | Valora mucho el futuro lejano; los valores crecen y la convergencia es más lenta. `γ=1` sin estado terminal → los retornos pueden diverger. |
| `ε` | Probabilidad de acción aleatoria; balance exploración/explotación. | Explora demasiado (casi aleatorio), no explota lo aprendido, política mala. `ε=1` → agente completamente aleatorio. |
