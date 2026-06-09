## ESP32 — Assets IoT

| Arquivo | Descrição |
|---------|-----------|
| `iot_data_flow.png` | Fluxo sensor → ESP32 → MQTT → API → Dashboard |

**Firmware:** [`src/hardware/esp32/field_node.ino`](../../src/hardware/esp32/field_node.ino)

**Demo no dashboard:** telemetria simulada com filtro de borda (anomalia ≥ 15% ou janela horária).

Para diagrama interativo Wokwi, importe o sketch e publique o link neste README após montar o circuito na turma.
