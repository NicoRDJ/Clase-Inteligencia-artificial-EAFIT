# Actividades de clase resueltas (Parte 1)

Actividades planteadas dentro de los slides del curso (`slides/claseN.md`), resueltas.
Las actividades que son notebooks con `TODO` están en `talleres/` y `notebooks/`.

---

## Clase 1 — Agentes racionales · clasificar entornos de tarea

> Slide: "¿Los siguientes entornos de tarea son totalmente observables? ¿determinísticos?
> ¿episódicos? ¿estáticos? ¿discretos? ¿de un solo agente? ¿conocidos?"
> (selección adaptada de AIMA 4.ª ed., Fig. 2.6)

| Entorno | Observable | Determinista | Episódico | Estático | Discreto | Un agente | Conocido |
|---|---|---|---|---|---|---|---|
| Crucigrama | Totalmente | Determinista | Secuencial | Estático | Discreto | Un agente | Conocido |
| Ajedrez con reloj | Totalmente | Determinista\* | Secuencial | Semi‑estático (reloj) | Discreto | Multiagente | Conocido |
| Póker | Parcialmente | Estocástico | Secuencial | Estático | Discreto | Multiagente | Conocido |
| Backgammon | Totalmente | Estocástico (dados) | Secuencial | Estático | Discreto | Multiagente | Conocido |
| Conducción de un taxi | Parcialmente | Estocástico | Secuencial | Dinámico | Continuo | Multiagente | Parcialmente conocido |
| Diagnóstico médico | Parcialmente | Estocástico | Secuencial | Dinámico | Continuo | Un agente | Parcialmente conocido |
| Robot part‑picking | Parcialmente | Estocástico | Episódico | Dinámico | Continuo | Un agente | Parcialmente conocido |
| ChatGPT | Parcialmente | Estocástico | Secuencial (con contexto) | Estático | Discreto (tokens) | Un agente\*\* | Parcialmente conocido |
| El mundo real | Parcialmente | Estocástico | Secuencial | Dinámico | Continuo | Multiagente | Parcialmente conocido |

\* El ajedrez es determinista en cuanto a las reglas; la incertidumbre viene del oponente, que se modela como parte del entorno (multiagente).
\*\* Si se le dan herramientas / otros agentes, pasa a multiagente.

**Idea clave:** el mejor diseño de agente depende del tipo de entorno. Entornos totalmente
observables, deterministas, discretos y estáticos permiten agentes simples (tablas/reglas);
entornos parcialmente observables, estocásticos, continuos y dinámicos exigen modelos del
mundo, manejo de incertidumbre y aprendizaje.

**¿Y Pac-Man?** Totalmente observable (el mapa completo se ve), determinista en la versión
clásica sin fantasmas aleatorios (estocástico si los fantasmas se mueven al azar),
secuencial, dinámico, discreto, multiagente (fantasmas), conocido.

---

## Clase 4 — MDP · calcular `V³(2,1)` a mano

> Slide "Actividad — calculen a mano, en parejas". Dada `V²` del Gridworld 4×3 después de
> la iteración 2, calcular `V³(s)` para `s = (2,1)` (la celda debajo del +0.7520, junto al
> terminal −1). Ruido 0.8 / 0.1 / 0.1, `R(s) = −0.04`, `γ = 1`.

```
V²:   -0.0800 | -0.0800 | +0.7520 | +1.0000
      -0.0800 |  WALL   | -0.0800 | -1.0000
      -0.0800 | -0.0800 | -0.0800 | -0.0800
```

Para cada acción `a`: `Q(s,a) = Σ_s' P(s'|s,a) · V²(s')`, con 0.8 a la dirección intentada
y 0.1 a cada perpendicular. `s = (2,1)`; vecinos: arriba `(2,2)=0.752`, abajo (borde → se
queda en `(2,1)=−0.08`)… usando el layout del slide:

```
Q(s, UP)    = 0.8·V(2,2) + 0.1·V(2,1) + 0.1·V(3,1)
            = 0.8(0.752) + 0.1(-0.08) + 0.1(-1.0)  = 0.4936   ← la mayor
Q(s, DOWN)  = 0.8·V(2,0) + 0.1·V(2,1) + 0.1·V(3,1) = -0.1720
Q(s, LEFT)  = 0.8·V(2,1) + 0.1·V(2,2) + 0.1·V(2,0) =  0.0032
Q(s, RIGHT) = 0.8·V(3,1) + 0.1·V(2,2) + 0.1·V(2,0) = -0.7328   ← ir directo al -1
```

```
V³(2,1) = R(s) + max_a Q(s,a) = -0.04 + 0.4936 = 0.4536
```

`UP` gana con claridad: aunque parezca "alejarse", es la única acción que **no** arriesga un
10 % de caer en el terminal −1. `RIGHT` (ir directo hacia el −1) da `Q = −0.7328`, clarísimamente
peor, porque el ruido del 20 % te puede tirar exactamente ahí aunque no sea la intención.

El mismo cálculo, hecho por código y extendido a un grid 5×6, está en
`notebooks/clase4-mdp/03_lab_warehouse_mdp_resuelto.ipynb`.
