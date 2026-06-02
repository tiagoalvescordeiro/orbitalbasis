## Models — Artefatos de ML

Pasta reservada ao template FIAP Global Solution. Os modelos e pipelines desta POC ficam em código em `src/ml_models/`.

### Implementação ativa

| Componente | Localização |
|------------|-------------|
| NDVI matricial (OpenCV) | `src/ml_models/ndvi_processor.py` |
| Facade `NDVIProcessor` | `src/core_logic/facades.py` |

### Uso

```bash
pytest tests/test_ndvi_processor.py -q
python scripts/run_demo.py
```

Artefatos treinados (se houver no futuro) devem ser versionados aqui ou ignorados via `.gitignore`; embeddings RAG ficam em `data/chroma_db/` (regenerável).
