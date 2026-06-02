# OrbitalBasis

Copiloto orbital de comercialização agrícola — **Global Solution FIAP 2026.1** (*A Nova Economia Espacial*).

Conecta **visão computacional** (NDVI matricial), **edge IoT** (ESP32 com filtragem de banda), **compliance ESG** (APP), **web scraping/API de mercado** (PTAX BCB + B3) e **motor de basis/PPE** com briefing RAG para cooperativas e mesas de operações.

> Material **educacional**. Não constitui recomendação de investimento.

---

## Arquitetura

```
Satélite (Red/NIR) → NDVIProcessor (OpenCV)
ESP32 (edge)       → TelemetryStore → API
BCB PTAX + B3 SJC  → MarketDataService → SojaBasisEngine
ESG APP            → ESGCompliance
OrbitalOrchestrator → FastAPI + Streamlit
```

---

## Quick start

```bash
cd orbitalbasis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -q
python scripts/run_demo.py
```

### API (distribuído)

```bash
uvicorn src.applications.api.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET/POST | `/api/v1/analysis` | Pipeline completo (`esg_red_flag`, `soil_moisture_pct`, `saca_rs`) |
| POST | `/api/v1/hardware/telemetry` | Ingestão pacote ESP32 (anomalia edge) |
| GET | `/api/v1/hardware/telemetry` | Últimos pacotes |

### Docker Compose (API + Dashboard)

```bash
copy .env.example .env
docker compose up --build
```

- API: http://localhost:8000/docs  
- Dashboard: http://localhost:8501  

### RAG (ChromaDB + LangChain)

```bash
python scripts/index_rag.py          # indexa knowledge/
python scripts/index_rag.py --force  # reindexar
```

| `ORBITAL_RAG_MODE` | Comportamento |
|--------------------|---------------|
| `deterministic` | Template fixo (demo offline) |
| `hybrid` (padrão) | Template + trechos Chroma |
| `llm` | LangChain + OpenAI se `OPENAI_API_KEY` definida |

### Dashboard (vídeo 5 min)

```bash
streamlit run src/applications/dashboard/app.py
```

Sidebar: **Simular Cenário de Risco ESG (Red Flag)**.

Modo API remota (opcional):

```bash
set ORBITAL_USE_API=true
set ORBITAL_API_URL=http://127.0.0.1:8000
streamlit run src/applications/dashboard/app.py
```

---

## Estrutura do repositório

```
src/
├── ml_models/ndvi_processor.py      # NDVI matricial + limiarização
├── core_logic/
│   ├── basis_engine.py              # Basis, PPE, curva, convergência
│   ├── esg_compliance.py            # Red flag APP
│   ├── orchestrator.py              # OrbitalOrchestrator
│   └── facades.py                   # SojaBasisEngine, NDVIProcessor, ...
├── market_data/
│   ├── ptax_client.py               # BCB OData + scrape + CSV
│   └── b3_client.py                 # B3 scrape + CSV
├── data_collection/serial_mqtt_reader.py
├── rag/commercial_copilot.py
├── applications/
│   ├── api/main.py
│   └── dashboard/app.py
└── hardware/esp32/field_node.ino
docs/VIDEO_SCRIPT.md
data/synthetic/                      # Fallback PTAX e B3
```

---

## Módulos principais (facades)

| Classe | Arquivo |
|--------|---------|
| `NDVIProcessor` | `ndvi_processor.py` |
| `SojaBasisEngine` | `basis_engine.py` |
| `ESGCompliance` | `esg_compliance.py` |
| `OrbitalOrchestrator` | `orchestrator.py` |

---

## Web scraping e fallbacks

1. **PTAX:** API OData BCB → scraping página BCB → `data/synthetic/ptax_history.csv`
2. **B3 SJC:** scraping página derivativos B3 → `data/synthetic/b3_quotes_sjc.csv`

Logs indicam a fonte utilizada (`bcb_odata`, `b3_scrape`, `csv_fallback`).

---

## Documentação

- [Arquitetura do sistema](docs/ARCHITECTURE.md)
- [Especificação da API REST](docs/API_SPECIFICATION.md)
- [Roteiro de vídeo 5 min](docs/VIDEO_SCRIPT.md)
- Fórmulas basis/PPE: `src/core_logic/basis_engine.py`
- Prompt RAG: `src/rag/prompts/briefing_template.txt`

---

## Equipe FIAP

| Nome | RM |
|------|-----|
| Tiago Alves Cordeiro | 561791 |
| Leandro Arthur Marinho Ferreira | 565240 |
| Otavio Custodio de Oliveira | 565606 |
| Matheus José Parra | 561907 |

---

## Licença

Projeto acadêmico — FIAP Global Solution 2026.1.
