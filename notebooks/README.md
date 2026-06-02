## Notebooks — Exploração e demonstração

Pasta do template oficial para Jupyter. Esta entrega prioriza scripts reproduzíveis e testes automatizados.

### Alternativas equivalentes no repositório

| Objetivo | Comando |
|----------|---------|
| Pipeline completo (demo) | `python scripts/run_demo.py` |
| API + dashboard | `scripts/start_all.ps1` ou `docker compose up` |
| Indexação RAG | `python scripts/index_rag.py` |
| Testes | `pytest tests/ -q` |

Notebooks opcionais podem ser adicionados aqui para EDA de NDVI ou curvas B3 sem substituir os módulos em `src/`.
