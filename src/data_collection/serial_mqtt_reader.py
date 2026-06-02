"""
Leitor de telemetria ESP32 — serial/MQTT simulado para dashboard.

Armazena pacotes edge-filtered em buffer thread-safe para exibição em tempo real.
"""

from __future__ import annotations

import json
import logging
import random
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Deque, Optional

logger = logging.getLogger(__name__)

MAX_LOG_LINES = 80


@dataclass
class TelemetryPacket:
    node: str
    soil_moisture_pct: float
    local_mean: float
    local_std: float
    tx_reason: str
    edge_filtered: bool = True
    received_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "node": self.node,
            "soil_moisture_pct": self.soil_moisture_pct,
            "local_mean": self.local_mean,
            "local_std": self.local_std,
            "tx_reason": self.tx_reason,
            "edge_filtered": self.edge_filtered,
            "received_at": self.received_at,
        }


class TelemetryStore:
    """Singleton de telemetria para API + Streamlit."""

    _instance: Optional["TelemetryStore"] = None

    def __new__(cls) -> "TelemetryStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_store()
        return cls._instance

    def _init_store(self) -> None:
        self._packets: Deque[TelemetryPacket] = deque(maxlen=MAX_LOG_LINES)
        self._lock = threading.Lock()
        self._sim_thread: Optional[threading.Thread] = None
        self._sim_running = False

    def push(self, packet: TelemetryPacket) -> None:
        with self._lock:
            self._packets.appendleft(packet)
        logger.info(
            "Telemetria [%s] umidade=%.1f%% motivo=%s",
            packet.node,
            packet.soil_moisture_pct,
            packet.tx_reason,
        )

    def push_from_json(self, payload: dict[str, Any]) -> TelemetryPacket:
        packet = TelemetryPacket(
            node=str(payload.get("node", "esp32_01")),
            soil_moisture_pct=float(payload["soil_moisture_pct"]),
            local_mean=float(payload.get("local_mean", 0)),
            local_std=float(payload.get("local_std", 0)),
            tx_reason=str(payload.get("tx_reason", "api_post")),
            edge_filtered=bool(payload.get("edge_filtered", True)),
        )
        self.push(packet)
        return packet

    def get_recent(self, limit: int = 15) -> list[dict[str, Any]]:
        with self._lock:
            return [p.to_dict() for p in list(self._packets)[:limit]]

    def latest_moisture(self) -> Optional[float]:
        recent = self.get_recent(1)
        return float(recent[0]["soil_moisture_pct"]) if recent else None

    def start_simulator(self, interval_sec: float = 8.0) -> None:
        if self._sim_running:
            return
        self._sim_running = True

        def _loop() -> None:
            moisture = 28.0
            while self._sim_running:
                moisture += random.uniform(-4, 4)
                moisture = max(12.0, min(45.0, moisture))
                mean = moisture - random.uniform(-2, 2)
                reason = "anomaly_15pct" if random.random() > 0.6 else "hourly_window"
                self.push(
                    TelemetryPacket(
                        node="esp32_01",
                        soil_moisture_pct=round(moisture, 2),
                        local_mean=round(mean, 2),
                        local_std=round(random.uniform(1, 3), 2),
                        tx_reason=reason,
                    )
                )
                time.sleep(interval_sec)

        self._sim_thread = threading.Thread(target=_loop, daemon=True, name="esp32-sim")
        self._sim_thread.start()
        logger.info("Simulador ESP32 iniciado (intervalo=%.1fs)", interval_sec)

    def stop_simulator(self) -> None:
        self._sim_running = False


def get_telemetry_store() -> TelemetryStore:
    return TelemetryStore()
