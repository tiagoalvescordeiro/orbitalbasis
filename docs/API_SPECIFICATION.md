# OrbitalBasis — Especificação da API REST

Versão: **1.0.0**  
Base: `http://localhost:8000` (local) · `http://api:8000` (Docker Compose)

---

## Convenções

- Content-Type: `application/json`
- Erros: HTTP 4xx/5xx com `{"detail": "mensagem"}`
- Material educacional — não é API de execução de ordens

---

## Endpoints

### Health

```
GET /health
```

**200**

```json
{ "status": "ok", "service": "orbitalbasis" }
```

---

### Análise completa

```
GET /api/v1/analysis
POST /api/v1/analysis
```

#### Parâmetros (query ou body POST)

| Nome | Tipo | Obrigatório | Default | Descrição |
|------|------|-------------|---------|-----------|
| `esg_red_flag` | boolean | não | `false` | Simula violação ESG em APP |
| `soil_moisture_pct` | number | não | `22.0` | Umidade solo (%); ignorado se houver telemetria recente |
| `saca_rs` | number | não | `138.50` | Preço físico R$/saca |

#### Exemplo POST

```bash
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{"esg_red_flag": false, "soil_moisture_pct": 22, "saca_rs": 138.5}'
```

#### Resposta 200 (estrutura)

```json
{
  "ndvi_summary": {
    "ndvi_mean": 0.34,
    "stress_pct_severe": 20.72,
    "yield_risk_hint": 64
  },
  "ndvi_overlay_png_b64": "<base64>",
  "esg": {
    "compliant": true,
    "red_flag": false,
    "message": "...",
    "app_stress_pct": 6.91
  },
  "basis": {
    "commodity": "soja",
    "basis_atual": 4.35,
    "basis_indicativo": 4.49,
    "curve_shape": "contango",
    "hedge_stance": "monitor_short_basis"
  },
  "futures_curve": {
    "labels": ["M1", "M2", "M3"],
    "prices": [1220, 1232, 1245]
  },
  "rag_context": { },
  "briefing_markdown": "### Briefing OrbitalBasis...",
  "market_meta": {
    "ptax_fonte": "bcb_odata",
    "b3_fonte": "csv_fallback"
  }
}
```

---

### Telemetria hardware

```
POST /api/v1/hardware/telemetry
```

#### Body

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `soil_moisture_pct` | number | sim |
| `node` | string | não (default `esp32_01`) |
| `local_mean` | number | não |
| `local_std` | number | não |
| `tx_reason` | string | não (`anomaly_15pct`, `hourly_window`, `api_post`) |
| `edge_filtered` | boolean | não |

#### Exemplo

```bash
curl -X POST http://localhost:8000/api/v1/hardware/telemetry \
  -H "Content-Type: application/json" \
  -d '{"soil_moisture_pct": 19.2, "tx_reason": "anomaly_15pct"}'
```

#### Resposta 200

```json
{
  "status": "accepted",
  "packet": { "node": "esp32_01", "soil_moisture_pct": 19.2, ... }
}
```

---

```
GET /api/v1/hardware/telemetry?limit=15
```

#### Resposta 200

```json
{
  "packets": [ { "node": "esp32_01", "soil_moisture_pct": 22.0, ... } ]
}
```

---

## Códigos de erro

| HTTP | Situação |
|------|----------|
| 400 | Payload telemetria inválido |
| 500 | Falha no orchestrator / mercado |

---

## Integração Streamlit

Variáveis de ambiente:

```env
ORBITAL_USE_API=true
ORBITAL_API_URL=http://127.0.0.1:8000
```

Sem API: dashboard chama `OrbitalOrchestrator` localmente.
