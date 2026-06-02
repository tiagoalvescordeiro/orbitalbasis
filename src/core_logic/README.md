## Motor de Negócio — Core Logic

Análise fundamentalista de commodities seguindo FMDAT27 — Derivativos Agrícolas FIAP.

### Arquivos

- `basis_engine.py` — Basis (soja/milho/boi), Flat FOB, PPE, Curva (Contango/Backwardation), Convergência
- `esg_compliance.py` — Check APP e Red Flag
- `orchestrator.py` — Orquestra: NDVI + ESG + Basis + RAG
- `facades.py` — Fachadas públicas

### Uso

```python
from src.core_logic.orchestrator import OrbitalOrchestrator

analysis = OrbitalOrchestrator().run()
print(analysis.basis.curve_shape)
```
