# Trabajo 2 — Algoritmos de búsqueda (grafos, laberintos y red de actores IMDb)

**Curso:** Inteligencia Artificial — EAFIT
**Actividad:** Implementación de BFS, Greedy Best-First Search y A* sobre tres problemas de búsqueda con la misma arquitectura general.

## Objetivo

Implementar y comparar los principales algoritmos de búsqueda no informados e informados (DFS, BFS, UCS, Greedy Best-First Search y A*) sobre tres representaciones distintas del mismo patrón general: un grafo con estados y aristas escritas a mano, un laberinto donde los vecinos se calculan a partir de la geometría de una cuadrícula, y una red de actores de IMDb donde los vecinos se derivan de una relación en tablas.

## Contenido

```
notebooks/clase2-busqueda/
├── 02_algoritmos_busqueda_grafo.ipynb   # BFS, Greedy y A* sobre el grafo A–H
├── 02_busqueda_en_laberintos.ipynb      # los mismos algoritmos sobre tres laberintos
├── 02_degrees_bfs.ipynb                 # BFS sobre la red de actores (Six Degrees of Kevin Bacon)
├── mazes/                               # maze1.txt, maze2.txt, maze3.txt
├── degrees/                             # dataset pequeño (16 personas) para desarrollo y pruebas
├── grafo.png, search_complexity.md, requirements.txt
```

El dataset completo de IMDb (~1 millón de personas, ~58 MB) usado en la sección de demostración a escala de `02_degrees_bfs.ipynb` no se incluye en el repositorio por su tamaño; se descarga desde el mismo enlace de Google Drive que indica el material del curso.

## 1. Grafo A–H (`02_algoritmos_busqueda_grafo.ipynb`)

Implementé:

- `QueueFrontier.remove()`: extracción FIFO (`self.frontier[0]`).
- `breadth_first_search(graph, start, goal)`: BFS clásico sobre `QueueFrontier`, revisando la meta al sacar el nodo de la frontier.
- `greedy_best_first_search(graph, heuristic, start, goal)`: `PriorityFrontier` con prioridad `h(n)` únicamente.
- `a_star_search(graph, heuristic, start, goal)`: igual que UCS pero con prioridad `g(n) + h(n)`, manteniendo `best_cost` para permitir mejorar una ruta ya encontrada.

**Resultados** (grafo `A → H`, meta `H`):

| Algoritmo | Camino | Costo |
|---|---|---:|
| DFS | A → B → D → H | — (no óptimo) |
| BFS | A → B → D → H | 5 (mínimas aristas: 3) |
| UCS | A → C → E → H | 6 |
| Greedy | A → C → E → H | 6 |
| A* | A → B → E → H | 5 |

Las tres pruebas (`assert`) incluidas en el notebook para BFS, Greedy y A* pasaron sin modificarlas.

## 2. Laberintos (`02_busqueda_en_laberintos.ipynb`)

Traduje la misma arquitectura reemplazando `graph[state]` por `maze.neighbors(state)` y la heurística tabulada por `manhattan(state, goal)`. Implementé las mismas cuatro piezas (`QueueFrontier.remove`, BFS, Greedy, A*) adaptadas a esa firma.

**Resultados sobre `maze1`:**

| Algoritmo | Costo | ¿Óptimo? |
|---|---:|---|
| DFS | 64 | No |
| BFS | 28 | Sí |
| UCS | 28 | Sí |
| Greedy | 32 | No |
| A* (Manhattan) | 28 | Sí |

El experimento con heurística no admisible (`w=3`) redujo los estados explorados de 141 a 52, pero el costo subió de 36 a 40 — evidencia directa de que sobreestimar `h(n)` acelera la búsqueda a costa de perder la garantía de optimalidad. La comparación sobre `maze1`, `maze2` y `maze3` y todas las aserciones del notebook pasaron sin cambios.

## 3. Six Degrees of Kevin Bacon (`02_degrees_bfs.ipynb`)

Implementé:

- `neighbors_for_person(person_id)`: para cada película en `people[person_id]["movies"]`, agrega `(movie_id, co_star_id)` por cada actor en `movies[movie_id]["stars"]`.
- `shortest_path(source, target)`: BFS con `Node(state, parent, action)`, revisando si un vecino es la meta **al generarlo** (antes de encolarlo), como pide el enunciado para evitar encolar nodos de más en un grafo de ~1 millón de personas.

**Resultados (dataset pequeño, 16 personas):**

- Kevin Bacon → Tom Hanks: 1 grado de separación (coincidieron en *Apollo 13*).
- Jack Nicholson → Bill Paxton: 2 grados de separación.
- Con el dataset completo de IMDb (1,044,499 personas, 344,276 películas), la carga toma ~12.5 s; la búsqueda en sí se resuelve en fracciones de segundo una vez los datos están en memoria.

Todas las pruebas públicas (`neighbors_for_person` y `shortest_path`) pasaron.

---

## Preguntas de cierre

### Grafo A–H

**¿Qué algoritmos garantizan el camino de menor número de aristas?**
BFS: expande nivel por nivel, así que la primera vez que alcanza la meta lo hace con el menor número de aristas posible, sin importar los costos de cada arista.

**¿Qué algoritmos garantizan el camino de menor costo?**
UCS siempre, y A* cuando la heurística es admisible. BFS solo lo garantiza si todos los costos son iguales.

**¿Por qué GBF puede encontrar un camino subóptimo?**
Porque prioriza únicamente `h(n)`, la estimación de lo que falta, y nunca considera `g(n)`, lo que ya costó llegar hasta ahí. Puede meterse por una rama que "parece" cercana a la meta aunque ya haya sido cara.

**¿Qué ocurre con A* si `h(n) = 0` para todos los nodos?**
La prioridad queda reducida a `g(n) + 0 = g(n)`, por lo que A* se comporta exactamente igual que UCS.

**¿Qué efecto tiene el orden de los vecinos en DFS y BFS?**
En DFS puede cambiar completamente la solución encontrada (profundidad y contenido del camino), porque sigue ciegamente la primera rama disponible. En BFS con costos desiguales no afecta el número de aristas de la primera solución, pero sí puede cambiar cuál solución concreta se reporta en caso de empate y el orden de expansión.

### Laberintos

**¿Qué algoritmos garantizan el camino de menor número de pasos / menor costo?**
Como cada paso cuesta 1 en el laberinto, "menor número de pasos" y "menor costo" coinciden: BFS, UCS y A* (heurística admisible) garantizan ambos.

**¿Por qué Greedy puede encontrar un camino subóptimo aunque explore muy pocos estados?**
Mismo motivo que en el grafo: al mirar solo `h(n)` (distancia Manhattan), puede entrar a un pasillo que geométricamente parece acercarse a la meta pero que en realidad obliga a un rodeo, sin nunca reconsiderar lo ya gastado en `g(n)`.

**¿Qué ocurre con A* si `h(n) = 0`? ¿En qué algoritmo se convierte?**
Se convierte en UCS: la prioridad pasa a depender únicamente del costo acumulado.

**¿Qué efecto tiene el orden en que `neighbors()` genera las direcciones sobre DFS y BFS?**
En DFS puede alterar drásticamente qué camino se sigue primero y por lo tanto su longitud. En BFS no cambia la longitud del camino óptimo (todas las aristas cuestan 1), pero sí el orden exacto de expansión y qué ruta concreta se reporta entre varias igualmente cortas.

### Six Degrees of Kevin Bacon

**¿Por qué BFS y no DFS? ¿Qué pasaría si usara DFS sobre `large`?**
BFS garantiza el camino con menos películas de por medio porque expande por niveles. DFS podría seguir una cadena de coprotagonistas arbitrariamente larga antes de retroceder, sin ninguna garantía de encontrar primero (ni de encontrar en un tiempo razonable) el camino más corto en un grafo de ~1 millón de personas.

**¿Por qué no tiene sentido plantear este problema con A* o Greedy? ¿Qué tendría que existir en los datos para que sí tuviera sentido?**
No hay una heurística admisible natural: estimar "qué tan cerca" está un actor de otro requeriría prácticamente ya conocer la estructura del grafo que se busca resolver. Tendría sentido si existiera, por ejemplo, información adicional (año de nacimiento, género de películas, país) que correlacionara de forma confiable con la distancia real en el grafo.

**La optimización de revisar la meta al generar el nodo, no al sacarlo, ¿por qué mejora el desempeño en un grafo de 1 millón de nodos?**
No cambia el algoritmo (sigue siendo BFS), pero evita encolar nodos que ya sabemos que son la meta y que tendrían que sacarse y procesarse después; en un grafo de ese tamaño, cada nodo que se evita encolar/desencolar es trabajo y memoria que no se gasta.

**¿Qué estructura de datos usarías para no repetir el cálculo de vecinos?**
Un diccionario de caché (`{person_id: set_de_vecinos}`) que memorice el resultado de `neighbors_for_person` la primera vez que se calcula para cada persona, evitando recorrer de nuevo sus películas y coprotagonistas en llamadas posteriores.

**¿Qué tienen en común las tres representaciones de vecinos (diccionario, `Maze.neighbors`, `neighbors_for_person`)?**
En los tres casos el estado determina completamente sus vecinos a través de alguna función o consulta — una tabla escrita a mano, la geometría de una cuadrícula, o una relación entre tablas — y el algoritmo de búsqueda que recorre la frontier no cambia en absoluto entre los tres problemas. Lo único que cambia es cómo, dado un estado, se obtiene la lista de vecinos.
