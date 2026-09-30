"""El router debe aprender la política óptima en un escenario donde la conocemos."""
import json

from jarvis.router.env import RouterEnv, load_results
from jarvis.router.features import NaiveBayes, PrivacyDetector
from jarvis.router.qlearning import QRouter, evaluate, fixed


def _escenario(tmp_path):
    """local: gratis, bueno en fácil (0.9) y malo en difícil (0.2).
    nube:  cuesta, buena en todo (0.95). Hay tareas privadas."""
    rows = []
    for i in range(30):
        diff = "easy" if i % 2 == 0 else "hard"
        priv = i % 5 == 0
        rows.append({"task_id": f"t{i}", "category": "matematicas", "difficulty": diff, "private": priv,
                     "brain": "local", "score": 0.9 if diff == "easy" else 0.2, "cost_usd": 0.0, "latency_s": 2.0})
        rows.append({"task_id": f"t{i}", "category": "matematicas", "difficulty": diff, "private": priv,
                     "brain": "nube", "score": 0.95, "cost_usd": 0.002, "latency_s": 2.0})
    p = tmp_path / "r.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    return load_results(p, ["local", "nube"])


def test_q_learning_aprende_la_politica_optima(tmp_path):
    outcomes, tasks = _escenario(tmp_path)
    env = RouterEnv(outcomes, tasks, ["local", "nube"], list(tasks), episode_len=10, daily_budget=1.0, lam=0.5)
    agent = QRouter(["local", "nube"], seed=1)
    agent.train(env, episodes=2000)
    pol = agent.policy()
    assert pol["matematicas|easy|False|alto"] == "local"   # fácil: el local basta y es gratis
    assert pol["matematicas|hard|False|alto"] == "nube"    # difícil: vale la pena pagar
    # evaluación: mejor que "siempre local" y sin fugas
    seqs = [[f"t{(i * 7 + k) % 30}" for k in range(10)] for i in range(20)]
    q = evaluate(agent, env, seqs)
    local = evaluate(fixed("local"), env, seqs)
    nube = evaluate(fixed("nube"), env, seqs)
    assert q["fugas privadas"] == 0 and nube["fugas privadas"] > 0
    assert q["calidad media"] > local["calidad media"]
    assert q["costo/día (USD)"] < nube["costo/día (USD)"]


def test_escudo_nunca_deja_salir_lo_privado(tmp_path):
    outcomes, tasks = _escenario(tmp_path)
    agent = QRouter(["local", "nube"], shield=True)
    assert agent.legal(("matematicas", "hard", True, "alto")) == ["local"]


def test_naive_bayes_y_detector():
    nb = NaiveBayes().fit(["cuanto es 3 por 4", "suma 10 mas 5", "escribe una funcion en python", "codigo que ordene"],
                          ["mate", "mate", "codigo", "codigo"])
    assert nb.predict("cuanto es 7 por 8") == "mate"
    assert nb.predict("funcion python que invierta") == "codigo"
    det = PrivacyDetector()
    assert det.is_private("Mi cédula es 1034987654")
    assert det.is_private("mi contraseña es abc")
    assert not det.is_private("¿Cuál es la capital de Australia?")
