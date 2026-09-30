"""Agente de Q-learning tabular para el router (semana 5) + políticas de referencia.

Actualización (off-policy):
    Q(s,a) ← Q(s,a) + α [ r + γ · max_a' Q(s',a') − Q(s,a) ]

Exploración ε-greedy con decaimiento. El "escudo" (shield) es una restricción
dura: en estados privados solo se permite la acción local. Es enmascarar
acciones, no aprenderlas: la privacidad no se negocia por recompensa.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path


class QRouter:
    def __init__(self, actions: list[str], *, alpha=0.2, gamma=0.9, eps=1.0, eps_min=0.05, eps_decay=0.995,
                 shield: bool = True, local: str = "local", seed: int = 0):
        self.actions, self.alpha, self.gamma = actions, alpha, gamma
        self.eps, self.eps_min, self.eps_decay = eps, eps_min, eps_decay
        self.shield, self.local = shield, local
        self.Q = defaultdict(lambda: {a: 0.0 for a in actions})
        self.rng = random.Random(seed)

    def legal(self, state) -> list[str]:
        return [self.local] if (self.shield and state[2]) else self.actions

    def act(self, state, greedy: bool = False) -> str:
        legales = self.legal(state)
        if not greedy and self.rng.random() < self.eps:
            return self.rng.choice(legales)
        q = self.Q[state]
        best = max(q[a] for a in legales)
        return self.rng.choice([a for a in legales if q[a] == best])

    def update(self, s, a, r, s2):
        target = r if s2 is None else r + self.gamma * max(self.Q[s2][b] for b in self.legal(s2))
        self.Q[s][a] += self.alpha * (target - self.Q[s][a])

    def train(self, env, episodes: int = 3000) -> list[float]:
        curva = []
        for _ in range(episodes):
            s, done, total = env.reset(), False, 0.0
            while not done:
                a = self.act(s)
                s2, r, done = env.step(a)
                self.update(s, a, r, s2)
                s, total = s2, total + r
            self.eps = max(self.eps_min, self.eps * self.eps_decay)
            curva.append(total)
        return curva

    def policy(self) -> dict:
        return {"|".join(map(str, s)): max(self.legal(s), key=lambda a: q[a]) for s, q in self.Q.items()}

    def save(self, path: Path):
        Path(path).write_text(json.dumps({"Q": {"|".join(map(str, s)): q for s, q in self.Q.items()},
                                          "actions": self.actions}, indent=1))


# ── Políticas de referencia (baselines) ─────────────────────────────────────
def fixed(brain):
    return lambda state, env: brain


def random_policy(seed=0):
    rng = random.Random(seed)
    return lambda state, env: rng.choice(env.brains)


def rule_based(strong: str, local: str = "local"):
    """Regla manual: privado → local; difícil → cerebro fuerte; fácil → local."""
    return lambda state, env: local if state[2] or state[1] == "easy" else strong


def evaluate(policy, env, sequences: list[list[str]]) -> dict:
    """Corre una política sobre secuencias fijas (las mismas para todas) y promedia."""
    tot = defaultdict(float)
    for seq in sequences:
        s, done, R = env.reset(seq), False, 0.0
        while not done:
            s, r, done = env.step(policy(s, env) if callable(policy) else policy.act(s, greedy=True))
            R += r
        for k, v in env.stats.items():
            tot[k] += v
        tot["recompensa"] += R
    n, pasos = len(sequences), sum(len(q) for q in sequences)
    return {"recompensa/día": tot["recompensa"] / n, "calidad media": tot["calidad"] / pasos,
            "costo/día (USD)": tot["costo"] / n, "latencia media (s)": tot["latencia"] / pasos,
            "fugas privadas": int(tot["fugas"]), "sin presupuesto": int(tot["sin_presupuesto"])}
