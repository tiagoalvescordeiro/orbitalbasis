#!/bin/bash
# OrbitalBasis — treino ML no Vertex AI Workbench (terminal JupyterLab)
# Uso: bash scripts/gcp_train_commands.sh
# Opcional: export GCS_BUCKET=gs://orbitalbasis-ml

set -euo pipefail

GCS_BUCKET="${GCS_BUCKET:-}"

echo "=== OrbitalBasis ML treino (GCP Workbench) ==="

if [ ! -d "orbitalbasis" ]; then
  git clone https://github.com/tiagoalvescordeiro/orbitalbasis.git
fi
cd orbitalbasis

pip install -q -r requirements.txt pandas pyarrow joblib scikit-learn

mkdir -p data/training models

if [ -n "$GCS_BUCKET" ] && [ -f "$(command -v gsutil)" ]; then
  echo "Baixando dataset do bucket..."
  gsutil cp "${GCS_BUCKET}/datasets/yield_risk_v1.parquet" data/training/ || true
fi

if [ ! -f data/training/yield_risk_v1.parquet ]; then
  echo "Gerando dataset sintético (8000 linhas)..."
  python scripts/generate_training_dataset.py --rows 8000
fi

echo "Treinando Random Forest..."
python scripts/train_yield_risk.py

cat models/yield_risk_v1_metrics.json

if [ -n "$GCS_BUCKET" ] && [ -f "$(command -v gsutil)" ]; then
  echo "Enviando modelo para GCS..."
  gsutil cp models/yield_risk_v1.joblib "${GCS_BUCKET}/models/"
  gsutil cp models/yield_risk_v1_metrics.json "${GCS_BUCKET}/models/"
fi

echo "=== Concluído. Pare a instância Workbench para economizar créditos. ==="
