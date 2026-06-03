from pathlib import Path

import numpy as np
import pytest

from src.core_logic.orchestrator import compute_yield_risk_score
from src.ml_models.yield_risk_predictor import (
    DEFAULT_MODEL_PATH,
    build_feature_vector,
    predict_yield_risk,
)


def test_build_feature_vector_shape():
    summary = {
        "ndvi_mean": 0.4,
        "ndvi_std": 0.1,
        "stress_pct_severe": 10.0,
        "stress_pct_attention": 20.0,
        "stress_pct_healthy": 70.0,
    }
    x = build_feature_vector(summary, 22.0)
    assert x.shape == (1, 6)


def test_heuristic_fallback_without_model(monkeypatch):
    monkeypatch.setattr(
        "src.ml_models.yield_risk_predictor.ml_enabled",
        lambda: False,
    )
    score = compute_yield_risk_score(50, 22.0, ndvi_summary={"ndvi_mean": 0.4})
    assert score == 50


def test_heuristic_soil_boost_without_model(monkeypatch):
    monkeypatch.setattr(
        "src.ml_models.yield_risk_predictor.ml_enabled",
        lambda: False,
    )
    score = compute_yield_risk_score(50, 15.0)
    assert score == 58


@pytest.mark.skipif(not DEFAULT_MODEL_PATH.exists(), reason="Modelo não treinado")
def test_ml_prediction_when_model_exists():
    summary = {
        "ndvi_mean": 0.35,
        "ndvi_std": 0.12,
        "stress_pct_severe": 25.0,
        "stress_pct_attention": 15.0,
        "stress_pct_healthy": 60.0,
    }
    pred = predict_yield_risk(summary, 20.0)
    assert pred is not None
    assert 0 <= pred <= 100
