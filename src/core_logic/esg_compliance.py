"""
Compliance ESG: cruzamento talhão x APP (Área de Preservação Permanente).

Detecta supressão / invasão simulada via change detection NDVI em polígono APP.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.ml_models.ndvi_processor import compute_ndvi_matrix, segment_ndvi, summarize_field


@dataclass
class ESGVerdict:
    compliant: bool
    red_flag: bool
    message: str
    app_stress_pct: float
    details: dict[str, Any]


def load_geojson_polygon(path: Path) -> np.ndarray | None:
    """
    Placeholder: retorna máscara retangular demo se GeoJSON não estiver parseado.

    Em produção, usar geopandas/shapely para rasterizar APP sobre o talhão.
    """
    if not path.exists():
        return None
    return None


def mask_polygon_bbox(
    shape: tuple[int, int],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> np.ndarray:
    """Máscara retangular normalizada (0-1) para demo de APP."""
    h, w = shape
    mask = np.zeros((h, w), dtype=bool)
    mask[
        int(h * y0) : int(h * y1),
        int(w * x0) : int(w * x1),
    ] = True
    return mask


def check_app_infringement(
    red: np.ndarray,
    nir: np.ndarray,
    app_mask: np.ndarray,
    severe_threshold_pct: float = 8.0,
) -> ESGVerdict:
    """
    Verifica se há estresse severo anormal dentro da APP (proxy de supressão).

    Args:
        red, nir: Bandas do recorte orbital.
        app_mask: Boolean mask da APP no mesmo shape.
        severe_threshold_pct: % mínimo de pixels SEVERE na APP para red flag.
    """
    ndvi = compute_ndvi_matrix(red, nir)
    labels = segment_ndvi(ndvi)
    app_pixels = np.sum(app_mask)
    if app_pixels == 0:
        return ESGVerdict(
            compliant=True,
            red_flag=False,
            message="APP não definida; ESG em modo permissivo (demo).",
            app_stress_pct=0.0,
            details={},
        )

    severe_in_app = np.sum((labels == 2) & app_mask)
    app_stress_pct = 100.0 * severe_in_app / app_pixels
    field_summary = summarize_field(ndvi, labels)

    if app_stress_pct >= severe_threshold_pct:
        msg = (
            "Propriedade inelegível para originação e travamento de hedge "
            "devido a inconformidade ESG (anomalia de vegetação em APP)."
        )
        return ESGVerdict(
            compliant=False,
            red_flag=True,
            message=msg,
            app_stress_pct=round(app_stress_pct, 2),
            details={"field_summary": field_summary},
        )

    return ESGVerdict(
        compliant=True,
        red_flag=False,
        message="APP dentro dos parâmetros ESG para originação (demo).",
        app_stress_pct=round(app_stress_pct, 2),
        details={"field_summary": field_summary},
    )


def demo_app_mask_from_shape(shape: tuple[int, int]) -> np.ndarray:
    """APP simulada no canto superior-direito (afastada do estresse central da demo)."""
    return mask_polygon_bbox(shape, 0.72, 0.0, 1.0, 0.28)


def draw_esg_overlay(
    overlay_bgr: np.ndarray,
    app_mask: np.ndarray,
    red_flag: bool,
) -> np.ndarray:
    """Contorno azul na APP; vermelho se red flag."""
    out = overlay_bgr.copy()
    contours, _ = cv2.findContours(
        app_mask.astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    color = (0, 0, 255) if red_flag else (255, 120, 0)
    cv2.drawContours(out, contours, -1, color, 2)
    return out
