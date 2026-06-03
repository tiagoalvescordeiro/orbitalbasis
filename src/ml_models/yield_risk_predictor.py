"""
Preditor ML de risco de safra (yield_risk_score 0-100).

Carrega Random Forest treinado em models/yield_risk_v1.joblib.
Se ausente ou ORBITAL_USE_ML_YIELD_RISK=false, o orchestrator usa heurística.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "yield_risk_v1.joblib"
DEFAULT_METRICS_PATH = PROJECT_ROOT / "models" / "yield_risk_v1_metrics.json"

FEATURE_COLUMNS = [
    "ndvi_mean",
    "ndvi_std",
    "stress_pct_severe",
    "stress_pct_attention",
    "stress_pct_healthy",
    "soil_moisture_pct",
]

_model_cache: Any = None
_metrics_cache: dict | None = None


def ml_enabled() -> bool:
    if os.getenv("ORBITAL_USE_ML_YIELD_RISK", "true").lower() == "false":
        return False
    return DEFAULT_MODEL_PATH.exists()


def get_model_metrics() -> dict | None:
    global _metrics_cache
    if _metrics_cache is not None:
        return _metrics_cache
    if not DEFAULT_METRICS_PATH.exists():
        return None
    try:
        _metrics_cache = json.loads(DEFAULT_METRICS_PATH.read_text(encoding="utf-8"))
        return _metrics_cache
    except Exception as exc:
        logger.warning("Métricas ML indisponíveis: %s", exc)
        return None


def _load_model() -> Any | None:
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    if not DEFAULT_MODEL_PATH.exists():
        return None
    try:
        import joblib

        _model_cache = joblib.load(DEFAULT_MODEL_PATH)
        logger.info("Modelo yield_risk carregado: %s", DEFAULT_MODEL_PATH.name)
        return _model_cache
    except Exception as exc:
        logger.warning("Falha ao carregar modelo yield_risk: %s", exc)
        return None


def build_feature_vector(
    ndvi_summary: dict,
    soil_moisture_pct: float,
) -> np.ndarray:
    """Vetor de features alinhado ao dataset de treino."""
    return np.array(
        [
            [
                float(ndvi_summary.get("ndvi_mean") or 0.0),
                float(ndvi_summary.get("ndvi_std") or 0.0),
                float(ndvi_summary.get("stress_pct_severe") or 0.0),
                float(ndvi_summary.get("stress_pct_attention") or 0.0),
                float(ndvi_summary.get("stress_pct_healthy") or 0.0),
                float(soil_moisture_pct),
            ]
        ],
        dtype=np.float64,
    )


def predict_yield_risk(
    ndvi_summary: dict,
    soil_moisture_pct: float,
) -> Optional[int]:
    """
    Retorna score 0-100 se o modelo estiver disponível; senão None (fallback heurístico).
    """
    if not ml_enabled():
        return None

    model = _load_model()
    if model is None:
        return None

    try:
        x = build_feature_vector(ndvi_summary, soil_moisture_pct)
        raw = float(model.predict(x)[0])
        return int(np.clip(round(raw), 0, 100))
    except Exception as exc:
        logger.warning("Predição ML yield_risk falhou: %s", exc)
        return None
