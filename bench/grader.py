"""Calificador automático del banco: cada respuesta recibe una nota en [0, 1]."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unicodedata


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def _numbers(text: str) -> list[float]:
    """Extrae números aceptando separadores de miles (1.450.000 / 1,450,000) y decimales."""
    out = []
    for tok in re.findall(r"-?\d[\d.,]*", text):
        t = tok.rstrip(".,")
        if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", t):          # 4.650.000 o 4,650,000
            t = re.sub(r"[.,]", "", t)
        elif t.count(",") == 1 and t.count(".") == 0:          # decimal con coma
            t = t.replace(",", ".")
        else:
            t = t.replace(",", "")
        try:
            out.append(float(t))
        except ValueError:
            pass
    return out


def grade_numeric(text: str, answer) -> float:
    nums = _numbers(text)
    if not nums:
        return 0.0
    target = float(answer)
    tol = max(abs(target) * 1e-3, 0.011)
    # la respuesta pide "solo el número": se evalúa el último número mencionado
    return 1.0 if abs(nums[-1] - target) <= tol else 0.0


def _extract_code(text: str) -> str:
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    return max(m, key=len) if m else text


def grade_code(text: str, answer: dict) -> float:
    """Ejecuta los tests en orden (conservando el estado entre ellos) y
    retorna la fracción de asserts que pasan."""
    code = _extract_code(text)
    body = []
    for t in answer["tests"]:
        if t.lstrip().startswith("assert"):
            body.append(f"try:\n    {t}\n    _ok += 1\nexcept Exception:\n    pass")
        else:
            body.append(f"try:\n    {t}\nexcept Exception:\n    pass")
    n_asserts = sum(t.lstrip().startswith("assert") for t in answer["tests"])
    program = code + "\n\n_ok = 0\n" + "\n".join(body) + "\nprint(_ok)\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(program)
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=10)
        passed = int(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else 0
    except (subprocess.TimeoutExpired, ValueError):
        passed = 0
    return passed / n_asserts


def grade_json(text: str, answer: dict) -> float:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return 0.0
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return 0.0
    ok = 0
    for k, v in answer.items():
        got = data.get(k)
        if isinstance(v, (int, float)):
            ok += isinstance(got, (int, float)) and float(got) == float(v) or str(got).strip() == str(v)
        else:
            ok += isinstance(got, str) and _norm(got).strip() == _norm(v).strip()
    return ok / len(answer)


def grade_contains(text: str, answer: list[str]) -> float:
    t = _norm(text)
    return 1.0 if any(_norm(a) in t for a in answer) else 0.0


def grade_format(text: str, rule: dict) -> float:
    t = text.strip()
    lines = [l for l in t.splitlines() if l.strip()]
    checks = []
    if "bullets" in rule:
        bullets = [l for l in lines if l.lstrip().startswith("- ")]
        checks.append(len(bullets) == rule["bullets"] and len(bullets) == len(lines))
        if "max_words_per_line" in rule:
            checks.append(all(len(l.lstrip()[2:].split()) <= rule["max_words_per_line"] for l in bullets))
    if rule.get("uppercase"):
        letters = [c for c in t if c.isalpha()]
        checks.append(bool(letters) and all(c.isupper() for c in letters))
    if "max_words" in rule:
        checks.append(len(t.split()) <= rule["max_words"])
    if "exact" in rule:
        checks.append(_norm(re.sub(r"[^\w]", "", t)) == _norm(rule["exact"]))
    if "lines" in rule:
        checks.append(len(lines) == rule["lines"])
    if "separator_count" in rule:
        sep, n = rule["separator_count"]
        parts = [p for p in t.split(sep)]
        checks.append(len(lines) == 1 and len(parts) == n and all(p.strip() == p and p for p in parts))
    if "int_range" in rule:
        lo, hi = rule["int_range"]
        checks.append(bool(re.fullmatch(r"\d+", t)) and lo <= int(t) <= hi)
    return sum(checks) / len(checks) if checks else 0.0


GRADERS = {"numeric": grade_numeric, "code": grade_code, "json": grade_json,
           "contains": grade_contains, "format": grade_format}


def grade(task: dict, text: str) -> float:
    if not text:
        return 0.0
    return float(GRADERS[task["grader"]](text, task["answer"]))
