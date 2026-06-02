## Módulo RAG — Copiloto de Comercialização

Briefing Markdown cruzando basis/PPE/curva com risco climático (NDVI + IoT).

### Arquivos

- `commercial_copilot.py` — Gera briefing (deterministic/hybrid/llm)
- `retriever.py` — Busca semântica ChromaDB
- `indexer.py` — Indexa documentos
- `prompts/briefing_template.txt` — Template FMDAT27

### Modos (ORBITAL_RAG_MODE)

- `deterministic` — Template fixo
- `hybrid` — Template + ChromaDB (padrão)
- `llm` — LangChain + OpenAI

### Uso

```python
from src.rag.commercial_copilot import generate_briefing_markdown

briefing = generate_briefing_markdown(rag_context_dict)
```
