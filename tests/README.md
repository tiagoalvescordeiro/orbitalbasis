## Testes automatizados

Validação do MVP OrbitalBasis (Global Solution FIAP 2026.1).

```bash
pytest tests/ -q
```

| Arquivo | Cobertura |
|---------|-----------|
| `test_ndvi_processor.py` | NDVI matricial, segmentação OpenCV |
| `test_yield_risk_ml.py` | Features ML, preditor, fallback heurístico |
| `test_basis_engine.py` | Basis, curva, convergência, bloqueio ESG |
| `test_market_data.py` | PTAX, B3, fallbacks |
| `test_rag_copilot.py` | Briefing RAG, modos deterministic/hybrid |

**Última execução:** 25 testes passando.
