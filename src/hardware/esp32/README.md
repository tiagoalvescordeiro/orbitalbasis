## Firmware ESP32 — Edge Computing

### Arquivo

- `field_node.ino` — Código Arduino ESP32

### Lógica

- Amostragem: 5s
- Média móvel + desvio padrão em tempo real
- Transmite MQTT apenas se: `|leitura - média|/média >= 15%` OU janela de 1h

### Config (ajustar no sketch)

- `WIFI_SSID`, `WIFI_PASS`, `MQTT_BROKER`, `MQTT_PORT`
- `WINDOW_SIZE=20`, `ANOMALY_PCT=0.15`
