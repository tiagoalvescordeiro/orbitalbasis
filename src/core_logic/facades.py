"""
Facades públicas — aliases esperados pela equipe / documentação FIAP.

Reexportam implementações existentes sem quebrar imports atuais.
"""

from __future__ import annotations

from src.core_logic.basis_engine import (
    BasisResult,
    MarketSnapshot,
    YieldContext,
    analyze_soja,
    analyze_milho,
)
from src.core_logic.esg_compliance import ESGVerdict, check_app_infringement
from src.core_logic.orchestrator import OrbitalAnalysis, OrbitalOrchestrator
from src.ml_models.ndvi_processor import NDVIResult, process_demo_synthetic, process_field


class SojaBasisEngine:
    """Motor de basis para soja (wrapper sobre analyze_soja)."""

    @staticmethod
    def analyze(
        market: MarketSnapshot,
        yield_ctx: YieldContext,
        futures_curve: list[float],
        contrato_futuro_usd_t: float = 400.0,
    ) -> BasisResult:
        return analyze_soja(market, yield_ctx, futures_curve, contrato_futuro_usd_t)


class NDVIProcessor:
    """Processador NDVI matricial (OpenCV + NumPy)."""

    process_field = staticmethod(process_field)
    process_demo = staticmethod(process_demo_synthetic)


class ESGCompliance:
    """Verificação ESG / APP."""

    check = staticmethod(check_app_infringement)


__all__ = [
    "SojaBasisEngine",
    "NDVIProcessor",
    "ESGCompliance",
    "OrbitalOrchestrator",
    "OrbitalAnalysis",
    "NDVIResult",
    "ESGVerdict",
]
