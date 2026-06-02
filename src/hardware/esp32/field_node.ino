/**
 * OrbitalBasis — Nó de campo ESP32 (Edge Computing)
 *
 * Filtragem na borda para economia de banda orbital/IoT:
 * - Média móvel e desvio padrão local de umidade do solo
 * - Transmissão apenas se |leitura - média| / média > 15% OU janela horária
 *
 * Hardware demo: DHT22 (umidade ar), pino analógico solo (simulado).
 */

#include <WiFi.h>
#include <PubSubClient.h>

// --- Configuração (ajustar no secrets.h ou platformio.ini) ---
const char* WIFI_SSID = "FIAP_DEMO";
const char* WIFI_PASS = "senha_demo";
const char* MQTT_BROKER = "192.168.1.100";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "orbitalbasis/field/node1";

const int PIN_SOIL = 34;
const int WINDOW_SIZE = 20;
const float ANOMALY_PCT = 0.15f;
const unsigned long HOURLY_MS = 3600000UL;  // 1h simulada (demo: 60000 = 1 min)

float buffer[WINDOW_SIZE];
int buffer_idx = 0;
int buffer_count = 0;
unsigned long last_tx_ms = 0;

WiFiClient wifi_client;
PubSubClient mqtt(wifi_client);

float read_soil_moisture_pct() {
  int raw = analogRead(PIN_SOIL);
  return constrain(map(raw, 0, 4095, 100, 0), 0.0f, 100.0f);
}

void buffer_push(float v) {
  buffer[buffer_idx] = v;
  buffer_idx = (buffer_idx + 1) % WINDOW_SIZE;
  if (buffer_count < WINDOW_SIZE) buffer_count++;
}

float buffer_mean() {
  if (buffer_count == 0) return 0.0f;
  float s = 0.0f;
  for (int i = 0; i < buffer_count; i++) s += buffer[i];
  return s / buffer_count;
}

float buffer_stddev(float mean) {
  if (buffer_count < 2) return 0.0f;
  float acc = 0.0f;
  for (int i = 0; i < buffer_count; i++) {
    float d = buffer[i] - mean;
    acc += d * d;
  }
  return sqrt(acc / (buffer_count - 1));
}

bool should_transmit(float current, float mean) {
  unsigned long now = millis();
  if (now - last_tx_ms >= HOURLY_MS) return true;
  if (buffer_count < 5) return false;
  if (mean < 1.0f) return true;
  float deviation = fabs(current - mean) / mean;
  return deviation >= ANOMALY_PCT;
}

void publish_packet(float moisture, float mean, float stddev, const char* reason) {
  char payload[256];
  snprintf(payload, sizeof(payload),
    "{\"node\":\"esp32_01\",\"soil_moisture_pct\":%.2f,\"local_mean\":%.2f,"
    "\"local_std\":%.2f,\"tx_reason\":\"%s\",\"edge_filtered\":true}",
    moisture, mean, stddev, reason);
  mqtt.publish(MQTT_TOPIC, payload);
  last_tx_ms = millis();
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SOIL, INPUT);
  analogSetAttenuation(ADC_11db);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.println("\nOrbitalBasis edge node online");
}

void loop() {
  if (!mqtt.connected()) {
    if (mqtt.connect("orbitalbasis_edge")) {
      Serial.println("MQTT connected");
    }
  }
  mqtt.loop();

  float moisture = read_soil_moisture_pct();
  buffer_push(moisture);
  float mean = buffer_mean();
  float std = buffer_stddev(mean);

  if (should_transmit(moisture, mean)) {
    const char* reason = (millis() - last_tx_ms >= HOURLY_MS) ? "hourly_window" : "anomaly_15pct";
    publish_packet(moisture, mean, std, reason);
  }

  delay(5000);  // amostragem local a cada 5s; transmissão filtrada
}
