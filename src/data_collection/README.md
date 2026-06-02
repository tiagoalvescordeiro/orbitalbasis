## Data Collection — Telemetria ESP32

Ingestão e buffer de pacotes edge-filtered vindos do firmware MQTT ou da API.

### Arquivos

- `serial_mqtt_reader.py` — `TelemetryStore`, simulador de pacotes, integração FastAPI/Streamlit

### Formato do pacote (JSON)

```json
{
  "node": "esp32_01",
  "soil_moisture_pct": 22.5,
  "local_mean": 21.0,
  "local_std": 1.2,
  "tx_reason": "anomaly_15pct",
  "edge_filtered": true
}
```

### Uso

**POST** na API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/hardware/telemetry \
  -H "Content-Type: application/json" \
  -d "{\"soil_moisture_pct\": 18.0, \"local_mean\": 22.0, \"local_std\": 2.1, \"tx_reason\": \"anomaly_15pct\"}"
```

Firmware de referência: `src/hardware/esp32/field_node.ino`.
