import numpy as np

from src.ml_models.ndvi_processor import (
    NDVIThresholds,
    StressClass,
    compute_ndvi_matrix,
    process_demo_synthetic,
    segment_ndvi,
)


def test_ndvi_formula_known_pixels():
    red = np.array([[100.0]], dtype=np.float32)
    nir = np.array([[200.0]], dtype=np.float32)
    ndvi = compute_ndvi_matrix(red, nir)
    expected = (200 - 100) / (200 + 100)
    assert np.isclose(ndvi[0, 0], expected, atol=1e-5)


def test_segmentation_three_classes():
    ndvi = np.array([[0.2, 0.45, 0.7]], dtype=np.float32)
    labels = segment_ndvi(ndvi, NDVIThresholds())
    assert labels[0, 0] == StressClass.SEVERE
    assert labels[0, 1] == StressClass.ATTENTION
    assert labels[0, 2] == StressClass.HEALTHY


def test_demo_pipeline_returns_summary():
    result = process_demo_synthetic(seed=1)
    assert "yield_risk_hint" in result.summary
    assert result.overlay_bgr.shape[0] == result.ndvi.shape[0]
