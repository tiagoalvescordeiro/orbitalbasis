"""
Orquestrador OrbitalBasis: NDVI (CV) + ESG + Basis + contexto RAG.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import asdict, dataclass
from typing import Any, Optional

import cv2
import numpy as np

from src.core_logic.basis_engine import (
    BasisResult,
    CurveShape,
    HedgeStance,
    MarketSnapshot,
    YieldContext,
    analyze_soja,
    to_rag_context,
)
from src.core_logic.esg_compliance import (
    check_app_infringement,
    demo_app_mask_from_shape,
    draw_esg_overlay,
)
from src.core_logic.esg_compliance import ESGVerdict
from src.market_data.market_service import MarketDataService
from src.ml_models.ndvi_processor import NDVIResult, process_demo_synthetic, process_field
from src.rag.commercial_copilot import generate_briefing_markdown

logger = logging.getLogger(__name__)


@dataclass
class OrbitalAnalysis:
    ndvi: NDVIResult
    esg: ESGVerdict
    esg_compliant: bool
    esg_message: str
    basis: BasisResult
    rag_context: dict
    briefing_markdown: str
    market_meta: dict
    futures_curve: list[float]
    overlay_esg_bgr: Optional[np.ndarray] = None


class OrbitalOrchestrator:
    """Orquestra pipeline completo com dados de mercado ao vivo ou fallback."""

    def __init__(self, market_service: Optional[MarketDataService] = None) -> None:
        self._market = market_service or MarketDataService()

    def run(
        self,
        soil_moisture_pct: float = 22.0,
        esg_red_flag_demo: bool = False,
        saca_rs: float = 138.50,
    ) -> OrbitalAnalysis:
        self._market._saca_rs = saca_rs
        market, futures_curve, market_meta = self._market.build_snapshot()

        stress_fraction = 0.32 if esg_red_flag_demo else 0.22
        ndvi_result = process_demo_synthetic(stress_fraction=stress_fraction)

        from src.ml_models.ndvi_processor import simulate_sentinel_bands

        red, nir = simulate_sentinel_bands(stress_fraction=stress_fraction)
        app_mask = demo_app_mask_from_shape(red.shape)

        if esg_red_flag_demo:
            # Força estresse dentro da APP para Red Flag cinematográfico
            app_mask = np.ones(red.shape, dtype=bool)
            red = red.copy()
            nir = nir.copy()
            red[app_mask] = np.clip(red[app_mask] + 80, 0, 255)
            nir[app_mask] = np.clip(nir[app_mask] - 100, 0, 255)
            ndvi_result = process_field(red, nir)

        esg = check_app_infringement(red, nir, app_mask)
        overlay_esg = draw_esg_overlay(ndvi_result.overlay_bgr, app_mask, esg.red_flag)

        yield_ctx = YieldContext(
            yield_risk_score=ndvi_result.summary["yield_risk_hint"],
            ndvi_mean=ndvi_result.summary["ndvi_mean"],
            soil_moisture_pct=soil_moisture_pct,
            esg_compliant=esg.compliant,
            esg_message=esg.message,
        )

        basis = analyze_soja(market, yield_ctx, futures_curve)
        rag = to_rag_context(basis, yield_ctx)
        rag["esg_app_stress_pct"] = esg.app_stress_pct
        rag["market_meta"] = market_meta

        briefing = generate_briefing_markdown(rag)
        logger.info(
            "Análise concluída: basis=%.2f ESG=%s curva=%s",
            basis.basis_atual,
            esg.compliant,
            basis.curve_shape.value,
        )

        return OrbitalAnalysis(
            ndvi=ndvi_result,
            esg=esg,
            esg_compliant=esg.compliant,
            esg_message=esg.message,
            basis=basis,
            rag_context=rag,
            briefing_markdown=briefing,
            market_meta=market_meta,
            futures_curve=futures_curve,
            overlay_esg_bgr=overlay_esg,
        )


def run_demo_analysis(
    market: MarketSnapshot | None = None,
    soil_moisture_pct: float = 22.0,
    esg_red_flag_demo: bool = False,
) -> OrbitalAnalysis:
    """Compatibilidade com scripts e testes legados."""
    if market is not None:
        return _run_legacy_manual_market(market, soil_moisture_pct, esg_red_flag_demo)
    return OrbitalOrchestrator().run(
        soil_moisture_pct=soil_moisture_pct,
        esg_red_flag_demo=esg_red_flag_demo,
    )


def _run_legacy_manual_market(
    market: MarketSnapshot,
    soil_moisture_pct: float,
    esg_red_flag_demo: bool,
) -> OrbitalAnalysis:
    stress_fraction = 0.32 if esg_red_flag_demo else 0.22
    ndvi_result = process_demo_synthetic(stress_fraction=stress_fraction)
    from src.ml_models.ndvi_processor import simulate_sentinel_bands

    red, nir = simulate_sentinel_bands(stress_fraction=stress_fraction)
    app_mask = demo_app_mask_from_shape(red.shape)
    esg = check_app_infringement(red, nir, app_mask)
    yield_ctx = YieldContext(
        yield_risk_score=ndvi_result.summary["yield_risk_hint"],
        ndvi_mean=ndvi_result.summary["ndvi_mean"],
        soil_moisture_pct=soil_moisture_pct,
        esg_compliant=esg.compliant,
        esg_message=esg.message,
    )
    futures_curve = [1220.0, 1232.0, 1245.0]
    basis = analyze_soja(market, yield_ctx, futures_curve)
    rag = to_rag_context(basis, yield_ctx)
    rag["esg_app_stress_pct"] = esg.app_stress_pct
    return OrbitalAnalysis(
        ndvi=ndvi_result,
        esg=esg,
        esg_compliant=esg.compliant,
        esg_message=esg.message,
        basis=basis,
        rag_context=rag,
        briefing_markdown=generate_briefing_markdown(rag),
        market_meta={},
        futures_curve=futures_curve,
    )


def _encode_image_bgr(img: np.ndarray) -> str:
    _, buf = cv2.imencode(".png", img)
    return base64.b64encode(buf.tobytes()).decode("ascii")


def analysis_to_dict(analysis: OrbitalAnalysis) -> dict[str, Any]:
    """Serialização JSON para API REST e dashboard remoto."""
    basis = analysis.basis
    overlay = analysis.overlay_esg_bgr if analysis.overlay_esg_bgr is not None else analysis.ndvi.overlay_bgr

    return {
        "ndvi_summary": analysis.ndvi.summary,
        "ndvi_overlay_png_b64": _encode_image_bgr(overlay),
        "esg": {
            "compliant": analysis.esg_compliant,
            "red_flag": analysis.esg.red_flag,
            "message": analysis.esg_message,
            "app_stress_pct": analysis.esg.app_stress_pct,
        },
        "basis": {
            "commodity": basis.commodity,
            "basis_atual": basis.basis_atual,
            "basis_indicativo": basis.basis_indicativo,
            "basis_unit": basis.basis_unit,
            "flat_fob_usd_t": basis.flat_fob_usd_t,
            "ppe_hint_rs_saca": basis.ppe_hint_rs_saca,
            "curve_shape": basis.curve_shape.value
            if isinstance(basis.curve_shape, CurveShape)
            else str(basis.curve_shape),
            "convergence_gap": basis.convergence_gap,
            "hedge_stance": basis.hedge_stance.value
            if isinstance(basis.hedge_stance, HedgeStance)
            else str(basis.hedge_stance),
            "narrative_hooks": basis.narrative_hooks,
        },
        "futures_curve": {
            "labels": ["M1", "M2", "M3"],
            "prices": analysis.futures_curve,
        },
        "rag_context": analysis.rag_context,
        "briefing_markdown": analysis.briefing_markdown,
        "market_meta": analysis.market_meta,
    }


def run_from_bands(
    red: np.ndarray,
    nir: np.ndarray,
    market: MarketSnapshot,
    futures_curve: list[float],
    soil_moisture_pct: float,
    app_mask: np.ndarray | None = None,
) -> OrbitalAnalysis:
    """Pipeline com bandas reais (satélite processado localmente)."""
    ndvi_result = process_field(red, nir)
    if app_mask is None:
        app_mask = demo_app_mask_from_shape(red.shape)

    esg = check_app_infringement(red, nir, app_mask)
    yield_ctx = YieldContext(
        yield_risk_score=ndvi_result.summary["yield_risk_hint"],
        ndvi_mean=ndvi_result.summary["ndvi_mean"],
        soil_moisture_pct=soil_moisture_pct,
        esg_compliant=esg.compliant,
        esg_message=esg.message,
    )
    basis = analyze_soja(market, yield_ctx, futures_curve)
    rag = to_rag_context(basis, yield_ctx)
    rag["esg_app_stress_pct"] = esg.app_stress_pct

    return OrbitalAnalysis(
        ndvi=ndvi_result,
        esg=esg,
        esg_compliant=esg.compliant,
        esg_message=esg.message,
        basis=basis,
        rag_context=rag,
        briefing_markdown=generate_briefing_markdown(rag),
        market_meta={},
        futures_curve=futures_curve,
        overlay_esg_bgr=draw_esg_overlay(ndvi_result.overlay_bgr, app_mask, esg.red_flag),
    )
