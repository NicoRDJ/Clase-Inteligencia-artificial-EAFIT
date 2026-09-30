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
        r"\bsaldo\b", r"\bcuenta de (ahorros|corriente|fondeo)\b", r"\bein\b", r"\bnequi\b",
        r"\bbancolombia\b", r"\bhistoria cl[ií]nica\b", r"\bmis gastos\b", r"\bmi usuario\b",
        r"\b\d{8,11}\b",                        # números largos: cédulas, cuentas, teléfonos
        r"\b\d{2,3}-\d{5,7}-\d{2}\b",           # formato de cuenta bancaria
        r"\b\d{2}-\d{7}\b",                     # EIN
    ]

    def __init__(self, nb: NaiveBayes | None = None):
        self.nb = nb
        self._re = [re.compile(p, re.IGNORECASE) for p in self.PATRONES]

    def rule_hit(self, text: str) -> bool:
        return any(r.search(text) for r in self._re)

    def is_private(self, text: str) -> bool:
        return self.rule_hit(text) or (self.nb is not None and self.nb.predict(text) == "privado")
