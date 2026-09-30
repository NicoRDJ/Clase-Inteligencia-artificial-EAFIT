"""Percepción del router: qué tipo de petición llegó y si contiene datos privados.

Todo implementado desde cero con técnicas de la Parte 1 del curso:
- `NaiveBayes`: clasificador multinomial con suavizado de Laplace (semana 7).
- `PrivacyDetector`: reglas (patrones) + Naive Bayes, combinados con OR para
  priorizar el *recall*: es preferible marcar de más que dejar escapar un dato.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter, defaultdict

_STOP = set("""de la el en y a los las un una que es por con para del al se lo como mas o
su sus me mi tu te le les nos este esta eso esto solo sin sobre entre cual cuanto cuantos
responde respuesta final numero únicamente unicamente nada explicacion""".split())


def tokenize(text: str) -> list[str]:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    toks = re.findall(r"[a-z]+|\d+", t)
    out = []
    for w in toks:
        if w.isdigit():
            out.append("<num>" if len(w) < 7 else "<num_largo>")   # cédulas, cuentas, montos
        elif w not in _STOP and len(w) > 1:
            out.append(w)
    return out


class NaiveBayes:
    """Naive Bayes multinomial: argmax_c  log P(c) + Σ_w log P(w | c)."""

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, texts: list[str], labels: list[str]) -> "NaiveBayes":
        self.classes = sorted(set(labels))
        self.prior = {c: math.log(labels.count(c) / len(labels)) for c in self.classes}
        self.counts: dict[str, Counter] = defaultdict(Counter)
        for text, y in zip(texts, labels):
            self.counts[y].update(tokenize(text))
        self.vocab = set().union(*self.counts.values())
        self.total = {c: sum(self.counts[c].values()) for c in self.classes}
        return self

    def log_scores(self, text: str) -> dict[str, float]:
        toks = tokenize(text)
        V = len(self.vocab)
        return {c: self.prior[c] + sum(math.log((self.counts[c][w] + self.alpha) / (self.total[c] + self.alpha * V))
                                       for w in toks if w in self.vocab)
                for c in self.classes}

    def predict(self, text: str) -> str:
        s = self.log_scores(text)
        return max(s, key=s.get)


class PrivacyDetector:
    """¿La petición contiene datos que no deben salir del computador?"""

    PATRONES = [
        r"\bc[eé]dula\b", r"\bcontrase[ñn]a\b", r"\bclave\b", r"\bpassword\b", r"\bpin\b",
        r"\bsaldo\b", r"\bcuenta de (ahorros|corriente|fondeo)\b", r"\bein\b",
        # un banco solo es privado en primera persona («tengo … en Nequi»), no como empleador en un texto
        r"\b(mi|mis|tengo|my)\b[^.?!]{0,50}\b(nequi|bancolombia|daviplata|davivienda)\b",
        r"\bhistoria cl[ií]nica\b", r"\bmis gastos\b", r"\bmi usuario\b",
        r"\bmis? (salario|sueldo|arriendo|cr[eé]dito|deuda|tarjeta|n[oó]mina|pensi[oó]n|ingresos|declaraci[oó]n de renta)s?\b",
        r"\b(gano|me pagan|debo)\b[^.?!]{0,30}\d",
        r"\b(mi|mis|tengo|gano|pago|debo)\b[^.?!]{0,60}\b\d{1,3}(?:\.\d{3}){2,}\b",   # montos personales en millones
        r"\bmy (password|pin|ssn|social security|bank account|balance|salary|medical)\b",
        r"\b(credit card|routing number|account number)\b",
        r"\b\d{8,11}\b",                        # números largos: cédulas, cuentas, teléfonos
        r"\b\d{2,3}-\d{5,7}-\d{2}\b",           # formato de cuenta bancaria
        r"\b\d{2}-\d{7}\b",                     # EIN
    ]

    def __init__(self, nb: NaiveBayes | None = None, margin: float = 4.0):
        self.nb, self.margin = nb, margin
        self._re = [re.compile(p, re.IGNORECASE) for p in self.PATRONES]

    def rule_hit(self, text: str) -> bool:
        return any(r.search(text) for r in self._re)

    def nb_hit(self, text: str) -> bool:
        """Naive Bayes solo marca privado si le gana a la segunda clase por `margin` nats
        (evita falsos positivos por frases comunes como «en una frase»)."""
        if self.nb is None or "privado" not in self.nb.classes:
            return False
        sc = self.nb.log_scores(text)
        otras = max(v for k, v in sc.items() if k != "privado")
        return sc["privado"] - otras >= self.margin

    def is_private(self, text: str) -> bool:
        return self.rule_hit(text) or self.nb_hit(text)


class DifficultyStump:
    """Árbol de decisión de un nivel por categoría: «difícil» si el texto supera un
    umbral de longitud aprendido (el que más aciertos da en entrenamiento).
    En 20 particiones aleatorias acierta 73 % vs. 59 % de un Naive Bayes de dificultad
    y 62 % del umbral fijo de 160 caracteres que usaba antes."""

    def fit(self, tasks: list[dict]) -> "DifficultyStump":
        self.thr: dict[str, int] = {}
        for c in {t["category"] for t in tasks}:
            L = [(len(t["prompt"]), t["difficulty"] == "hard") for t in tasks if t["category"] == c]
            self.thr[c] = max(sorted({l for l, _ in L}), key=lambda x: sum((l >= x) == h for l, h in L))
        self.default = sorted(self.thr.values())[len(self.thr) // 2]
        return self

    def predict(self, text: str, category: str) -> str:
        return "hard" if len(text) >= self.thr.get(category, self.default) else "easy"


class Perception:
    """Lo que el router *ve* de una petición: (categoría, dificultad, privada).

    Es lo mismo que usa JARVIS en vivo, así que el notebook evalúa el sistema de
    punta a punta: si el Naive Bayes se equivoca de categoría o el detector deja
    pasar un dato privado, el error se propaga a la decisión y se mide.
    - categoría: Naive Bayes de intención;
    - dificultad: un umbral de longitud por categoría (árbol de decisión de un nivel);
    - privada: reglas + Naive Bayes con margen. Si es privada, la categoría es «privado».
    """

    def __init__(self, tasks: list[dict], margin: float = 4.0):
        self.intent = NaiveBayes().fit([t["prompt"] for t in tasks], [t["category"] for t in tasks])
        self.difficulty = DifficultyStump().fit(tasks)
        self.privacy = PrivacyDetector(self.intent, margin)

    def __call__(self, text: str) -> tuple[str, str, bool]:
        private = self.privacy.is_private(text)
        if private:
            category = "privado"
        else:   # sin dato privado detectado, la mejor categoría no privada
            sc = self.intent.log_scores(text)
            category = max((c for c in sc if c != "privado"), key=sc.get)
        return category, self.difficulty.predict(text, category), private
