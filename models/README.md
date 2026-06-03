## Models — Artefatos de ML

### Treino local (recomendado para FIAP)

```bash
python scripts/generate_training_dataset.py
python scripts/train_yield_risk.py
```

| Artefato | Descrição |
|----------|-----------|
| `yield_risk_v1.joblib` | Random Forest — risco de safra 0–100 |
| `yield_risk_v1_metrics.json` | MAE, R², features |

Ver `docs/ML_GETTING_STARTED.md`.

### Implementação em código

| Componente | Localização |
|------------|-------------|
| NDVI (OpenCV) | `src/ml_models/ndvi_processor.py` |
| Preditor ML | `src/ml_models/yield_risk_predictor.py` |

Embeddings RAG: `data/chroma_db/` (regenerável, ver `.gitignore`).
