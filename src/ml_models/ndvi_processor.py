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
    seed: int | None = None,
    commodity: str = "soja",
    variation_factor: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gera bandas Red/NIR sintéticas realistas para demo.
    Desenha "talhões" (lotes agrícolas) e aplica blur Gaussiano
    para simular a irregularidade orgânica do solo/estresse hídrico.
    """
    rng = np.random.default_rng(seed)
    
    red_img = np.full((height, width), 130, dtype=np.uint8)
    nir_img = np.full((height, width), 100, dtype=np.uint8)
    
    # Factor ajusta a amplitude do ruído e o tamanho dos objetos
    vf = max(0.2, min(2.0, variation_factor))  # limita entre 0.2‑2.0
    
    if commodity == "soja":
        # Soja: Talhões densos, tamanhos e posições randômicas
        for _ in range(rng.integers(2, 5)):
            x, y = rng.integers(5, width-50), rng.integers(5, height-50)
            w, h = rng.integers(int(80*vf), int(160*vf)), rng.integers(int(80*vf), int(160*vf))
            cv2.rectangle(red_img, (int(x), int(y)), (int(x + w), int(y + h)), int(rng.integers(50, 75)), -1)
            cv2.rectangle(nir_img, (int(x), int(y)), (int(x + w), int(y + h)), int(rng.integers(180, 220)), -1)
        # Pivô central randômico
        if rng.random() > 0.3:
            cx, cy = rng.integers(100, width-50), rng.integers(100, height-50)
            radius = rng.integers(int(40*vf), int(80*vf))
            cv2.circle(red_img, (int(cx), int(cy)), int(radius), 45, -1)
            cv2.circle(nir_img, (int(cx), int(cy)), int(radius), 230, -1)
    elif commodity == "milho":
        # Milho: linhas com espaçamento, inclinação variável e largura variável
        angle_deg = float(rng.uniform(-15, 15))
        line_spacing = rng.integers(int(20*vf), int(45*vf))
        line_width = rng.integers(int(10*vf), int(25*vf))
        
        # Desenhando linhas e rotacionando a imagem para fazer as fileiras
        temp_red = np.full((height*2, width*2), 130, dtype=np.uint8)
        temp_nir = np.full((height*2, width*2), 100, dtype=np.uint8)
        
        for i in range(0, width*2, int(line_spacing)):
            cv2.line(temp_red, (i, 0), (i, height*2), int(rng.integers(70, 110)), int(line_width))
            cv2.line(temp_nir, (i, 0), (i, height*2), int(rng.integers(140, 180)), int(line_width))
            
        M = cv2.getRotationMatrix2D((width, height), angle_deg, 1.0)
        red_img = cv2.warpAffine(temp_red, M, (width, height))
        nir_img = cv2.warpAffine(temp_nir, M, (width, height))
        
    elif commodity == "cafe":
        # Café: Curvas de nível orgânicas
        cx, cy = rng.integers(int(width*0.3), int(width*0.7)), rng.integers(int(height*0.3), int(height*0.7))
        angle_offset = rng.integers(0, 360)
        for radius in range(20, int(width*1.2), rng.integers(int(20*vf), int(40*vf))):
            angle = int(angle_offset + rng.integers(-10, 10))
            cv2.ellipse(red_img, (int(cx), int(cy)), (int(radius), int(radius*0.7)), angle, 0, 360, 50, int(rng.integers(8, 16)))
            cv2.ellipse(nir_img, (int(cx), int(cy)), (int(radius), int(radius*0.7)), angle, 0, 360, 220, int(rng.integers(8, 16)))
    elif commodity == "boi":
        # Boi: Pastagem irregular / solo exposto
        for _ in range(rng.integers(1, 4)):
            num_pts = rng.integers(6, 12)
            # Create a localized blob of points for polygon
            cx, cy = rng.integers(30, width-30), rng.integers(30, height-30)
            rad = rng.integers(30, 100)
            pts = []
            for _ in range(num_pts):
                pts.append([rng.integers(cx-rad, cx+rad), rng.integers(cy-rad, cy+rad)])
            pts = np.array(pts, np.int32)
            pts = cv2.convexHull(pts)
            cv2.fillPoly(red_img, [pts], int(rng.integers(70, 90)))
            cv2.fillPoly(nir_img, [pts], int(rng.integers(160, 200)))
            
        # Áreas de pisoteio/bebedouro
        for _ in range(rng.integers(1, 4)):
            cx, cy = rng.integers(20, width-20), rng.integers(20, height-20)
            cv2.circle(red_img, (int(cx), int(cy)), int(rng.integers(15, 45)), 130, -1)
            cv2.circle(nir_img, (int(cx), int(cy)), int(rng.integers(15, 45)), 110, -1)
    
    red = red_img.astype(np.float32)
    nir = nir_img.astype(np.float32)
    
    # Máscara orgânica usando Gaussian Blur gigante em ruído aleatório
    # Para criar "manchas" irregulares de estresse hídrico pelo terreno
    noise = rng.integers(0, 255, (height, width), dtype=np.uint8)
    blob = cv2.GaussianBlur(noise, (111, 111), 0).astype(np.float32)
    blob_norm = (blob - blob.min()) / (blob.max() - blob.min() + 1e-6)
    
    # Adiciona "stress" orgânico: Aumenta o Vermelho e diminui o Infravermelho
    # Amplifica a variação orgânica com stress_fraction
    stress_mag = 50 + (stress_fraction * 150)
    red = np.clip(red + (blob_norm * stress_mag * vf), 0, 255)
    nir = np.clip(nir - (blob_norm * stress_mag * 1.5 * vf), 0, 255)
    
    return red, nir


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
    if red.shape != nir.shape:
        raise ValueError(
            f"Bandas Red e NIR devem ter a mesma resolução: {red.shape} vs {nir.shape}"
        )
    if red.size == 0:
        raise ValueError("Bandas vazias — nada a processar.")
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
