# Treino ML no Google Cloud (Vertex AI Workbench)

Caminho **simples e barato**: 1 instância CPU + Cloud Storage. Sem GPU.

## Pré-requisitos

1. Projeto GCP com billing ativo (créditos FIAP/educação).
2. APIs habilitadas: **Vertex AI API**, **Notebooks API**, **Cloud Storage API**.
3. Dataset local (no PC):

```powershell
python scripts/generate_training_dataset.py --rows 8000
```

## Passo 1 — Bucket no Cloud Storage

1. Console → **Cloud Storage** → **Buckets** → **Create**
2. Nome: `orbitalbasis-ml-SEU_ID` (global, standard)
3. Upload: `data/training/yield_risk_v1.parquet` → pasta `datasets/`

## Passo 2 — Vertex AI Workbench (instância)

1. Console → **Vertex AI** → **Workbench** → **Instances**
2. **Create new** → tipo **Single user**
3. Máquina: **e2-standard-2** (2 vCPU, 8 GB) — suficiente para Random Forest
4. Região: `us-central1` ou `southamerica-east1` (São Paulo)
5. **Create** (leva ~5–10 min)

## Passo 3 — Treinar no notebook

Abra **JupyterLab** na instância e no terminal:

```bash
git clone https://github.com/tiagoalvescordeiro/orbitalbasis.git
cd orbitalbasis
pip install -r requirements.txt pandas pyarrow joblib scikit-learn

# Se subiu o Parquet no bucket (ajuste BUCKET):
# gsutil cp gs://SEU_BUCKET/datasets/yield_risk_v1.parquet data/training/

python scripts/train_yield_risk.py
```

Baixe o modelo treinado:

```bash
# Na instância, após treino:
gsutil cp models/yield_risk_v1.joblib gs://SEU_BUCKET/models/
gsutil cp models/yield_risk_v1_metrics.json gs://SEU_BUCKET/models/
```

No PC local:

```powershell
gsutil cp gs://SEU_BUCKET/models/yield_risk_v1.joblib models/
gsutil cp gs://SEU_BUCKET/models/yield_risk_v1_metrics.json models/
```

## Passo 4 — Parar instância (economizar créditos)

Workbench → instância → **Stop** quando não estiver usando.

## Custo estimado (ordem de grandeza)

| Item | Uso típico FIAP |
|------|------------------|
| Workbench e2-standard-2 | ~US$ 0,07/h (parado = storage mínimo) |
| GCS | centavos para Parquet + joblib |
| **Total demo** | < US$ 1 se desligar após 1–2 h |

## Alternativa zero-console

Instale [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) no Windows e siga `scripts/gcp_train_commands.sh` para autenticação e jobs no Vertex.
