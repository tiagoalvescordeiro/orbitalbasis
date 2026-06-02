"""
Processamento de NDVI a partir de bandas espectrais (Visão Computacional).

Calcula NDVI na matriz (NIR - Red) / (NIR + Red), classifica estresse por
limiarização e gera mapa segmentado para o dashboard (verde / amarelo / vermelho).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np


class StressClass(IntEnum):
    HEALTHY = 0
    ATTENTION = 1
    SEVERE = 2


@dataclass(frozen=True)
class NDVIThresholds:
    """Limiares NDVI [-1, 1] para segmentação triclass."""

    severe_max: float = 0.35
    attention_max: float = 0.55

    def classify_value(self, ndvi: float) -> StressClass:
        if ndvi < self.severe_max:
            return StressClass.SEVERE
        if ndvi < self.attention_max:
            return StressClass.ATTENTION
        return StressClass.HEALTHY


# BGR para overlay no dashboard (OpenCV)
STRESS_COLORS_BGR = {
    StressClass.HEALTHY: (0, 180, 0),
    StressClass.ATTENTION: (0, 220, 255),
    StressClass.SEVERE: (0, 0, 220),
}


def compute_ndvi_matrix(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    NDVI pixel a pixel: (NIR - Red) / (NIR + Red).

    Args:
        red: Canal vermelho (float ou uint), mesma shape que nir.
        nir: Canal infravermelho próximo.

    Returns:
        Matriz NDVI em float32, valores em [-1, 1]; NaN onde denominador ~ 0.
    """
    red_f = red.astype(np.float32)
    nir_f = nir.astype(np.float32)
    denom = nir_f + red_f
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = np.where(denom > 1e-6, (nir_f - red_f) / denom, np.nan)
    return np.clip(ndvi, -1.0, 1.0)


def load_multiband_tiff(red_path: Path, nir_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Carrega bandas Red e NIR de arquivos GeoTIFF/PNG (escala 0-255 ou reflectância)."""
    red = cv2.imread(str(red_path), cv2.IMREAD_UNCHANGED)
    nir = cv2.imread(str(nir_path), cv2.IMREAD_UNCHANGED)
    if red is None or nir is None:
        raise FileNotFoundError(f"Bandas não encontradas: {red_path}, {nir_path}")
    if red.shape != nir.shape:
        raise ValueError("Bandas Red e NIR devem ter a mesma resolução.")
    return red, nir


def simulate_sentinel_bands(
    height: int = 256,
    width: int = 256,
    stress_fraction: float = 0.25,
    seed: int | None = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gera bandas Red/NIR sintéticas para demo sem API (POC / testes).

    Região central com menor NDVI simula estresse hídrico.
    """
    rng = np.random.default_rng(seed)
    # Baseline saudável: NDVI ~ 0.65–0.75 (NIR >> Red)
    red = rng.integers(70, 95, (height, width), dtype=np.uint16)
    nir = rng.integers(180, 220, (height, width), dtype=np.uint16)

    cy, cx = height // 2, width // 2
    y, x = np.ogrid[:height, :width]
    radius = int(min(height, width) * stress_fraction)
    mask = ((x - cx) ** 2 + (y - cy) ** 2) < radius**2
    red[mask] = np.clip(red[mask] + 55, 0, 255)
    nir[mask] = np.clip(nir[mask] - 90, 0, 255)
    return red.astype(np.float32), nir.astype(np.float32)


def segment_ndvi(
    ndvi: np.ndarray,
    thresholds: NDVIThresholds | None = None,
) -> np.ndarray:
    """
    Limiarização triclass do NDVI.

    Returns:
        Máscara int8 com valores StressClass (0, 1, 2).
    """
    th = thresholds or NDVIThresholds()
    valid = np.isfinite(ndvi)
    labels = np.full(ndvi.shape, StressClass.HEALTHY, dtype=np.int8)
    labels[valid & (ndvi < th.attention_max) & (ndvi >= th.severe_max)] = StressClass.ATTENTION
    labels[valid & (ndvi < th.severe_max)] = StressClass.SEVERE
    return labels


def build_stress_overlay(
    labels: np.ndarray,
    alpha: float = 0.55,
    base_bgr: np.ndarray | None = None,
) -> np.ndarray:
    """Mapa colorido verde / amarelo / vermelho para exibição no dashboard."""
    h, w = labels.shape
    if base_bgr is None:
        base_bgr = np.full((h, w, 3), 40, dtype=np.uint8)
    else:
        base_bgr = base_bgr.copy()

    overlay = np.zeros_like(base_bgr)
    for stress, color in STRESS_COLORS_BGR.items():
        mask = labels == int(stress)
        overlay[mask] = color

    return cv2.addWeighted(base_bgr, 1 - alpha, overlay, alpha, 0)


def summarize_field(ndvi: np.ndarray, labels: np.ndarray) -> dict:
    """Métricas agregadas para basis_engine e RAG."""
    valid = np.isfinite(ndvi)
    if not np.any(valid):
        return {
            "ndvi_mean": None,
            "ndvi_std": None,
            "stress_pct_severe": 0.0,
            "stress_pct_attention": 0.0,
            "stress_pct_healthy": 0.0,
            "yield_risk_hint": 0,
        }

    mean_ndvi = float(np.nanmean(ndvi[valid]))
    std_ndvi = float(np.nanstd(ndvi[valid]))
    total = int(np.sum(valid))
    severe = int(np.sum(labels == StressClass.SEVERE))
    attention = int(np.sum(labels == StressClass.ATTENTION))
    healthy = int(np.sum(labels == StressClass.HEALTHY))

    severe_pct = 100.0 * severe / total
    attention_pct = 100.0 * attention / total
    healthy_pct = 100.0 * healthy / total

    # 0-100: maior = mais risco de quebra regional
    yield_risk_hint = int(
        np.clip(severe_pct * 1.2 + attention_pct * 0.4 + (0.6 - mean_ndvi) * 30, 0, 100)
    )

    return {
        "ndvi_mean": round(mean_ndvi, 4),
        "ndvi_std": round(std_ndvi, 4),
        "stress_pct_severe": round(severe_pct, 2),
        "stress_pct_attention": round(attention_pct, 2),
        "stress_pct_healthy": round(healthy_pct, 2),
        "yield_risk_hint": yield_risk_hint,
    }


@dataclass
class NDVIResult:
    ndvi: np.ndarray
    labels: np.ndarray
    overlay_bgr: np.ndarray
    summary: dict


def process_field(
    red: np.ndarray,
    nir: np.ndarray,
    thresholds: NDVIThresholds | None = None,
    generate_overlay: bool = True,
) -> NDVIResult:
    """Pipeline completo: NDVI → limiarização → overlay → resumo."""
    ndvi = compute_ndvi_matrix(red, nir)
    labels = segment_ndvi(ndvi, thresholds)
    overlay = build_stress_overlay(labels) if generate_overlay else np.zeros((1, 1, 3), np.uint8)
    summary = summarize_field(ndvi, labels)
    return NDVIResult(ndvi=ndvi, labels=labels, overlay_bgr=overlay, summary=summary)


def process_from_files(red_path: Path, nir_path: Path) -> NDVIResult:
    red, nir = load_multiband_tiff(red_path, nir_path)
    return process_field(red, nir)


def process_demo_synthetic(**kwargs) -> NDVIResult:
    red, nir = simulate_sentinel_bands(**kwargs)
    return process_field(red, nir)


def export_ndvi_report_png(
    red: np.ndarray,
    nir: np.ndarray,
    output_path: Path,
    thresholds: NDVIThresholds | None = None,
) -> Path:
    """Gera e salva overlay color-coded como PNG para apresentações."""
    result = process_field(red, nir, thresholds)
    cv2.imwrite(str(output_path), result.overlay_bgr)
    return output_path


def adaptive_threshold_from_stddev(
    ndvi: np.ndarray,
    std_multiplier: float = 1.0,
) -> NDVIThresholds:
    """Threshold dinâmico baseado no desvio padrão do talhão."""
    valid = np.isfinite(ndvi)
    if not np.any(valid):
        return NDVIThresholds()
    mean = float(np.nanmean(ndvi[valid]))
    std = float(np.nanstd(ndvi[valid]))
    severe_max = np.clip(mean - std_multiplier * std, -1.0, 0.8)
    attention_max = np.clip(mean + std_multiplier * std, severe_max + 0.05, 1.0)
    return NDVIThresholds(severe_max=float(severe_max), attention_max=float(attention_max))
