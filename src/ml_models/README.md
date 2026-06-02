## Módulo de Visão Computacional — ML Models

Processamento matricial de NDVI a partir de bandas Red e NIR utilizando OpenCV e NumPy.

### Arquivos

- `__init__.py` — Expõe NDVIProcessor, StressClass
- `ndvi_processor.py` — Pipeline: compute_ndvi_matrix → segment_ndvi (verde/amarelo/vermelho) → build_stress_overlay → summarize_field

### Uso

```python
from src.ml_models.ndvi_processor import process_field, process_demo_synthetic

result = process_demo_synthetic()
print(result.summary["yield_risk_hint"])
```
