## Applications — Camada distribuída

API REST e dashboard que consomem o `OrbitalOrchestrator`.

| App | Arquivo | Execução |
|-----|---------|----------|
| API | `api/main.py` | `uvicorn src.applications.api.main:app --reload --port 8000` |
| Dashboard | `dashboard/app.py` | `streamlit run src/applications/dashboard/app.py` |

Modo distribuído (dashboard → API):

```bash
set ORBITAL_USE_API=true
set ORBITAL_API_URL=http://127.0.0.1:8000
```

Ver também `docker-compose.yml` na raiz do projeto.
