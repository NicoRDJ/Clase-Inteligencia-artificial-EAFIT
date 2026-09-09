# Clase 3 — Optimización (notebooks resueltos)

Notebooks de clase con las **actividades (`TODO`) completadas**. Cada uno es el
notebook original del curso; solo se rellenaron las celdas de actividad. Todos
corren de principio a fin y las celdas de prueba (`assert`) pasan.

| Notebook | Tema | Actividades resueltas |
|---|---|---|
| `01_hill_climbing_resuelto.ipynb` | Hill Climbing + Random Restart (ubicación de hospitales) | distancia euclídea; experimento con `k ∈ {1..5}` hospitales |
| `02_simulated_annealing_resuelto.ipynb` | Simulated Annealing (función 1-D multimodal) | barrido de temperatura inicial `T₀ ∈ {0.01…10}` |
| `02_simulated_annealing_hospitales_resuelto.ipynb` | SA sobre el problema discreto de hospitales | `T₀`; tasa de enfriamiento `α`; comparación justa HC vs SA en 50 estados |
| `03_algoritmos_geneticos_resuelto.ipynb` | GA sobre OneMax | selección por ruleta; cruce uniforme |
| `03_algoritmos_geneticos_hospitales_resuelto.ipynb` | GA sobre hospitales | mutación global; cruce uniforme con reparación; con/sin elitismo |
| `04_programacion_lineal_resuelto.ipynb` | LP con `scipy.optimize.linprog` | restricción de almacenamiento `4x₁+2x₂≤160` + gráfica |
| `05_csp_resuelto.ipynb` | CSP de horarios (backtracking, MRV, forward checking) | dominio de 2 días (sin solución); restricción unaria `A=Lunes`; LCV |
| `06_workshop_reinas_resuelto.ipynb` | **Workshop** N reinas (N=4): hill climbing, random restart, SA | las 8 actividades + comparación de éxito (100 corridas) |

> Nota: se aplicó un arreglo menor de compatibilidad (`plt.boxplot(labels=…)` →
> `tick_labels=…`) para matplotlib ≥ 3.9.
