## Scripts — Automação e demo

Utilitários para subir o ecossistema, indexar RAG e validar a POC.

| Script | Descrição |
|--------|-----------|
| `run_demo.py` | Executa pipeline OrbitalOrchestrator (terminal) |
| `index_rag.py` | Indexa `data/rag/knowledge/` no ChromaDB |
| `start_all.ps1` | Sobe API (uvicorn) e dashboard (Streamlit) no Windows |
| `run_dashboard_api.ps1` | Dashboard em modo distribuído (consome FastAPI em :8000) |
| `generate_training_dataset.py` | Gera Parquet para ML (yield_risk) |
| `train_yield_risk.py` | Treina Random Forest local (sem GCP) |
| `publish_github.ps1` | Publicação auxiliar no GitHub |
| `generate_entrega_pdf.py` | Gera PDF de entrega FIAP (`docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf`) |

### Exemplos

```bash
python scripts/run_demo.py
python scripts/index_rag.py --force
pytest tests/ -q
```

Variáveis úteis: `ORBITAL_RAG_MODE`, `ORBITAL_USE_API`, `ORBITAL_API_URL` (ver `.env.example`).
