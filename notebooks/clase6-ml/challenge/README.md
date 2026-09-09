# Clase 6 — Challenge de ML: pipeline de clasificación de vinos (resuelto)

Los tres notebooks se ejecutan **en orden** y comparten artefactos:

| Notebook | Hace | Produce |
|---|---|---|
| `01_data_challenge_resuelto.ipynb` | carga y valida `data/raw/wine.csv`, split estratificado 80/20, EDA solo sobre train | `data/processed/train.csv`, `test.csv`, `artifacts/data_contract.json` |
| `02_training_challenge_resuelto.ipynb` | pipelines con preprocesamiento dentro, CV estratificada, `GridSearchCV`, selección del campeón | `artifacts/champion_model.joblib`, `training_metadata.json`, `reports/cv_results.csv` |
| `03_evaluation_deployment_challenge_resuelto.ipynb` | abre el test una sola vez, métricas finales, función `predict` con validación de esquema, inferencia por lotes | `reports/test_metrics.json`, `batch_predictions.csv` |

**Resultado:** campeón = LogisticRegression · CV accuracy ≈ 0.979 · test accuracy ≈ 0.972 ·
F1 macro ≈ 0.971 (coherente con CV → sin sobreajuste).

Requiere: `scikit-learn`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `joblib`.
Los artefactos generados están en `.gitignore` (se recrean al ejecutar).
