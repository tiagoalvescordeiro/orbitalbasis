# ML local — Risco de safra (yield_risk)

Treino **sem Google Cloud** (zero crédito). Roda no seu PC em poucos minutos.

## O que o modelo faz

Prevê **risco de safra (0–100)** a partir de:

- NDVI médio e desvio
- % estresse severo / atenção / saudável
- Umidade do solo

O label de treino usa a **mesma heurística** do projeto (professor sintético). Depois vocês podem trocar por dados reais.

## Passo a passo

```powershell
cd orbitalbasis
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Gerar ~8000 linhas (Parquet local)
python scripts/generate_training_dataset.py

# 2) Treinar Random Forest
python scripts/train_yield_risk.py

# 3) Validar
python -m pytest tests/test_yield_risk_ml.py -q
python scripts/run_demo.py
```

Artefatos:

| Arquivo | Descrição |
|---------|-----------|
| `data/training/yield_risk_v1.parquet` | Dataset (não versionado no Git) |
| `models/yield_risk_v1.joblib` | Modelo |
| `models/yield_risk_v1_metrics.json` | MAE e R² |

## Uso no sistema

Com o `.joblib` presente, o orchestrator usa ML automaticamente.

Desativar ML (só heurística):

```env
ORBITAL_USE_ML_YIELD_RISK=false
```

## Próximo passo (GCP — opcional)

Quando quiserem usar créditos: subir o Parquet para **Cloud Storage** e rodar o mesmo `train_yield_risk.py` no **Vertex AI Workbench** (CPU barata). Não é obrigatório para a FIAP.
