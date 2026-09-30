"""
SI3003 - Inteligencia Artificial | Examen 01 - Componente practico (30%)
Plantilla de Q-learning tabular sobre un gridworld pequeno tipo Pac-Man.

Uso: es una PLANTILLA de estudio. El dia del examen te dan el ambiente
(step/reset/render) ya implementado y tu pegas / adaptas las tres piezas
del agente: epsilon_greedy(), update_q() y el bucle de entrenamiento.

Este archivo corre tal cual:  python "4 - Plantilla codigo Q-learning (practico).py"
(requiere numpy y matplotlib; si no hay matplotlib, comenta la Actividad 5)

Nicolas Rodriguez - 8 de septiembre de 2026
"""

from collections import defaultdict
import random

import numpy as np

# --------------------------------------------------------------------------
# 0) AMBIENTE  (el dia del examen esto te lo dan hecho; aqui va incluido para
#    que la plantilla sea ejecutable y puedas practicar el patron completo)
# --------------------------------------------------------------------------
RANDOM_STATE = 42
random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

ROWS, COLS = 4, 5
START = (3, 0)
GOAL = (0, 4)            # comida / meta:  recompensa +10, termina el episodio
GHOST = (1, 3)           # fantasma:       recompensa -10, termina el episodio
WALLS = {(1, 1), (2, 1), (2, 3)}
ACTIONS = ["up", "down", "left", "right"]
DELTA = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
STEP_COST = -0.1         # cada movimiento normal cuesta -0.1


def reset():
    """Devuelve el estado inicial."""
    return START


def step(state, action):
    """Ejecuta una accion. Devuelve (next_state, reward, done)."""
    dr, dc = DELTA[action]
    nxt = (state[0] + dr, state[1] + dc)

    # fuera del tablero o contra pared -> te quedas donde estabas
    if not (0 <= nxt[0] < ROWS and 0 <= nxt[1] < COLS):
        nxt = state
    if nxt in WALLS:
        nxt = state

    if nxt == GOAL:
        return nxt, 10.0, True
    if nxt == GHOST:
        return nxt, -10.0, True
    return nxt, STEP_COST, False


def is_blocked(s):
    return s in WALLS


def is_terminal(s):
    return s == GOAL or s == GHOST


# --------------------------------------------------------------------------
# 1) POLITICA epsilon-greedy
#    - con probabilidad epsilon: accion aleatoria (EXPLORACION)
#    - con probabilidad 1 - epsilon: argmax_a Q(s,a) (EXPLOTACION), desempate al azar
# --------------------------------------------------------------------------
def epsilon_greedy(Q, state, epsilon):
    if random.random() < epsilon:
        return random.choice(ACTIONS)                      # exploracion
    q_vals = [Q[(state, a)] for a in ACTIONS]
    best = max(q_vals)
    mejores = [a for a, q in zip(ACTIONS, q_vals) if q == best]
    return random.choice(mejores)                          # explotacion (con desempate)


# --------------------------------------------------------------------------
# 2) ACTUALIZACION DE Q-LEARNING
#    target   = r                         si done  (s' terminal -> sin futuro)
#             = r + gamma * max_a' Q(s',a')  en otro caso
#    td_error = target - Q(s,a)
#    Q(s,a)  += alpha * td_error
# --------------------------------------------------------------------------
def update_q(Q, state, action, reward, next_state, done, alpha, gamma):
    if done:
        target = reward
    else:
        target = reward + gamma * max(Q[(next_state, a)] for a in ACTIONS)
    td_error = target - Q[(state, action)]
    Q[(state, action)] += alpha * td_error
    return td_error


# --------------------------------------------------------------------------
# 3) ENTRENAMIENTO
#    - un episodio = desde START hasta terminal (o max_steps)
#    - epsilon decae linealmente de epsilon_start a epsilon_end
#    - guarda la recompensa total de cada episodio para la curva de aprendizaje
# --------------------------------------------------------------------------
def train_q_learning(episodes=3000, alpha=0.2, gamma=0.95,
                     epsilon_start=1.0, epsilon_end=0.05, max_steps=100):
    Q = defaultdict(float)
    episode_rewards = []

    for ep in range(episodes):
        # decaimiento lineal de epsilon
        frac = ep / max(1, episodes - 1)
        epsilon = epsilon_start + frac * (epsilon_end - epsilon_start)

        state = reset()
        total = 0.0
        for _ in range(max_steps):
            action = epsilon_greedy(Q, state, epsilon)
            next_state, reward, done = step(state, action)
            update_q(Q, state, action, reward, next_state, done, alpha, gamma)
            total += reward
            state = next_state
            if done:
                break
        episode_rewards.append(total)

    return Q, episode_rewards


# --------------------------------------------------------------------------
# 4) POLITICA GREEDY APRENDIDA:  para cada estado no terminal / no pared,
#    la accion de mayor Q.
# --------------------------------------------------------------------------
def greedy_policy(Q):
    policy = {}
    for r in range(ROWS):
        for c in range(COLS):
            s = (r, c)
            if is_blocked(s) or is_terminal(s):
                continue
            q_vals = [Q[(s, a)] for a in ACTIONS]
            policy[s] = ACTIONS[int(np.argmax(q_vals))]
    return policy


def show_policy(policy):
    arrows = {"up": "^", "down": "v", "left": "<", "right": ">"}
    for r in range(ROWS):
        fila = []
        for c in range(COLS):
            s = (r, c)
            if s in WALLS:
                fila.append("#")
            elif s == GOAL:
                fila.append("G")
            elif s == GHOST:
                fila.append("X")
            else:
                fila.append(arrows[policy[s]])
        print(" ".join(fila))


# --------------------------------------------------------------------------
# 5) EJECUTAR LA POLITICA FINAL SIN EXPLORACION (epsilon = 0)
# --------------------------------------------------------------------------
def run_greedy_episode(Q, max_steps=30):
    state = reset()
    trajectory = [state]
    total = 0.0
    for _ in range(max_steps):
        action = epsilon_greedy(Q, state, epsilon=0.0)
        state, reward, done = step(state, action)
        trajectory.append(state)
        total += reward
        if done:
            break
    return trajectory, total


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
if __name__ == "__main__":
    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)

    Q, episode_rewards = train_q_learning()

    print("Promedio recompensa - primeros 100 episodios:", round(np.mean(episode_rewards[:100]), 3))
    print("Promedio recompensa - ultimos  100 episodios:", round(np.mean(episode_rewards[-100:]), 3))
    print()

    print("Politica aprendida:")
    show_policy(greedy_policy(Q))
    print()

    traj, total = run_greedy_episode(Q)
    print("Trayectoria politica final:", traj)
    print("Recompensa total:", round(total, 2))
    print("Termino en:", "META (+10)" if traj[-1] == GOAL else ("FANTASMA (-10)" if traj[-1] == GHOST else "sin terminar"))

    # --- curva de aprendizaje (comenta este bloque si no tienes matplotlib) ---
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        rewards = pd.Series(episode_rewards)
        plt.plot(rewards.rolling(100).mean())
        plt.xlabel("Episodio")
        plt.ylabel("Recompensa promedio movil (ventana 100)")
        plt.title("Curva de aprendizaje del agente Q-learning")
        plt.tight_layout()
        plt.savefig("curva_aprendizaje.png", dpi=110)
        print("\nCurva guardada en curva_aprendizaje.png")
    except ImportError:
        print("\n(matplotlib/pandas no disponibles: se omite la curva)")

# ==========================================================================
# NOTAS PARA EL DIA DEL EXAMEN
# ==========================================================================
# - Si el ambiente usa indices de accion (0,1,2,3) en vez de strings, cambia
#   ACTIONS y usa range(env.n_actions) / np.argmax sobre un vector Q[s].
# - Si el estado es un entero codificado (env muy grande), Q puede ser
#   np.zeros((n_states, n_actions)) en vez de un defaultdict.
# - max_a' Q(s',a') SIEMPRE es 0 si s' es terminal -> por eso el 'if done'.
# - Desempate aleatorio en el argmax: importa para que la exploracion inicial
#   no quede sesgada hacia la primera accion de la lista.
# - Verifica con Kernel > Restart & Run All antes de enviar.
