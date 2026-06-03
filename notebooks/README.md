## Notebooks — Exploração e demonstração

Pasta do template oficial para Jupyter. Esta entrega prioriza scripts reproduzíveis e testes automatizados.

### Alternativas equivalentes no repositório

| Objetivo | Comando |
|----------|---------|
| Pipeline completo (demo) | `python scripts/run_demo.py` |
| API + dashboard | `scripts/start_all.ps1` ou `docker compose up` |
| Indexação RAG | `python scripts/index_rag.py` |
| Testes | `pytest tests/ -q` |

| Treino ML **gratuito (Colab)** | `train_yield_risk_colab.ipynb` + `docs/ML_COLAB_GRATUITO.md` |
| Treino ML no GCP (pago / créditos) | `train_yield_risk_vertex.ipynb` + `docs/ML_VERTEX_GCP.md` |

Notebooks opcionais podem ser adicionados aqui para EDA de NDVI ou curvas B3 sem substituir os módulos em `src/`.
