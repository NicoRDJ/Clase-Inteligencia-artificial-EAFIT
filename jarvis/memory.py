"""Memoria persistente de JARVIS (SQLite, local).

- `messages`: historial de conversación por sesión (quién habló, qué cerebro respondió,
  costo y latencia) → sirve de contexto y de registro para seguir entrenando el router.
- `facts`: hechos que Nico le pide recordar ("recuerda que...").
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "jarvis.db"


class Memory:
    def __init__(self, path: Path = DB):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY, ts REAL, session TEXT, role TEXT, text TEXT,
                brain TEXT, category TEXT, private INTEGER, cost REAL, latency REAL);
            CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, ts REAL, text TEXT);
        """)

    def add(self, session, role, text, *, brain=None, category=None, private=False, cost=0.0, latency=0.0):
        self.db.execute("INSERT INTO messages (ts, session, role, text, brain, category, private, cost, latency) "
                        "VALUES (?,?,?,?,?,?,?,?,?)",
                        (time.time(), session, role, text, brain, category, int(private), cost, latency))
        self.db.commit()

    def history(self, session, turns: int = 6) -> list[tuple[str, str]]:
        rows = self.db.execute("SELECT role, text FROM messages WHERE session=? ORDER BY id DESC LIMIT ?",
                               (session, turns * 2)).fetchall()
        return rows[::-1]

    def remember(self, text: str):
        self.db.execute("INSERT INTO facts (ts, text) VALUES (?, ?)", (time.time(), text))
        self.db.commit()

    def facts(self) -> list[str]:
        return [r[0] for r in self.db.execute("SELECT text FROM facts ORDER BY id").fetchall()]

    def spent_today(self) -> float:
        start = time.time() - (time.time() % 86400)
        return self.db.execute("SELECT COALESCE(SUM(cost),0) FROM messages WHERE ts >= ?", (start,)).fetchone()[0]
