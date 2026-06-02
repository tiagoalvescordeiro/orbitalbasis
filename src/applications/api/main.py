"""
API Gateway OrbitalBasis — FastAPI.

Endpoints:
  GET/POST /api/v1/analysis
  POST     /api/v1/hardware/telemetry
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core_logic.orchestrator import OrbitalOrchestrator, analysis_to_dict
from src.data_collection.serial_mqtt_reader import TelemetryPacket, get_telemetry_store
from src.market_data.ancord_defaults import DEFAULT_SACA_RS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbitalbasis.api")

app = FastAPI(
    title="OrbitalBasis API",
    description="Global Solution FIAP 2026.1 — Economia Espacial aplicada ao agro",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrator = OrbitalOrchestrator()
_telemetry = get_telemetry_store()


class AnalysisRequest(BaseModel):
    esg_red_flag: bool = Field(False, description="Simula violação APP / Red Flag ESG")
    soil_moisture_pct: float = Field(22.0, ge=0, le=100)
    saca_rs: float = Field(DEFAULT_SACA_RS, gt=0)
    use_telemetry_soil: bool = Field(
        False,
        description="Se true, substitui soil_moisture_pct pela última leitura ESP32",
    )


class TelemetryPayload(BaseModel):
    node: str = "esp32_01"
    soil_moisture_pct: float
    local_mean: float = 0.0
    local_std: float = 0.0
    tx_reason: str = "api_post"
    edge_filtered: bool = True


@app.on_event("startup")
def startup() -> None:
    _telemetry.start_simulator(interval_sec=12.0)
    try:
        from src.rag.indexer import ensure_index

        ensure_index()
        logger.info("Índice ChromaDB RAG pronto")
    except Exception as exc:
        logger.warning("RAG index skip: %s", exc)
    logger.info("OrbitalBasis API iniciada — simulador ESP32 ativo")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "orbitalbasis"}


@app.get("/api/v1/analysis")
@app.post("/api/v1/analysis")
def run_analysis(
    esg_red_flag: bool = Query(False),
    soil_moisture_pct: float = Query(22.0),
    saca_rs: float = Query(DEFAULT_SACA_RS),
    use_telemetry_soil: bool = Query(
        False,
        description="Substituir umidade manual pela última leitura ESP32",
    ),
    body: Optional[AnalysisRequest] = None,
) -> dict[str, Any]:
    try:
        if body is not None:
            esg_red_flag = body.esg_red_flag
            soil_moisture_pct = body.soil_moisture_pct
            saca_rs = body.saca_rs
            use_telemetry_soil = body.use_telemetry_soil

        if use_telemetry_soil or os.getenv("ORBITAL_USE_TELEMETRY_SOIL", "").lower() == "true":
            moisture = _telemetry.latest_moisture()
            if moisture is not None:
                soil_moisture_pct = moisture

        analysis = _orchestrator.run(
            soil_moisture_pct=soil_moisture_pct,
            esg_red_flag_demo=esg_red_flag,
            saca_rs=saca_rs,
        )
        return analysis_to_dict(analysis)
    except Exception as exc:
        logger.exception("Falha em /api/v1/analysis")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/hardware/telemetry")
def ingest_telemetry(payload: TelemetryPayload) -> dict[str, Any]:
    try:
        packet = _telemetry.push_from_json(payload.model_dump())
        return {"status": "accepted", "packet": packet.to_dict()}
    except Exception as exc:
        logger.exception("Falha em telemetria")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/hardware/telemetry")
def list_telemetry(limit: int = Query(15, ge=1, le=50)) -> dict[str, Any]:
    return {"packets": _telemetry.get_recent(limit)}
