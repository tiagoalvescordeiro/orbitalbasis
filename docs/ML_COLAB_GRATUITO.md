# Treino ML gratuito — Google Colab

Sem Vertex AI Workbench (sem custo por hora de VM).

## Passo a passo

1. Abra https://colab.research.google.com (conta Google gratuita).
2. **Arquivo → Abrir notebook → GitHub**
3. Cole: `https://github.com/tiagoalvescordeiro/orbitalbasis`
4. Abra: `notebooks/train_yield_risk_colab.ipynb`
5. Menu **Runtime → Executar tudo** (ou `Ctrl+F9`).
6. Aguarde ~5–10 minutos.
7. Na última célula, baixe `yield_risk_v1.joblib` e `yield_risk_v1_metrics.json`.
8. Copie os arquivos para `models/` na pasta do projeto no seu PC.

## Alternativa: upload do notebook

Baixe o arquivo `notebooks/train_yield_risk_colab.ipynb` do repositório e faça upload no Colab.

## Para a apresentação FIAP

> Treinamos um Random Forest para estimar risco de safra (0–100) a partir de NDVI e umidade do solo, com pipeline reproduzível no Colab (custo zero) e integração ao OrbitalBasis via `yield_risk_predictor.py`.

## Treino local (também gratuito)

```powershell
python scripts/generate_training_dataset.py --rows 8000
python scripts/train_yield_risk.py
```
