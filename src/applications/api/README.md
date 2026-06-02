## API REST — FastAPI

### Como rodar

```bash
uvicorn src.applications.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/analysis` | Pipeline completo |
| POST | `/api/v1/hardware/telemetry` | Ingestão ESP32 |
| GET | `/api/v1/hardware/telemetry` | Últimos pacotes |
