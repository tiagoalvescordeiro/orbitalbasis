"""
Motor de Basis, PPE e alinhamento com curva de futuros (FMDAT27 / Saint Paul).

Implementa:
- Basis físico vs contrato futuro (soja, milho, boi)
- Flat FOB e PPE simplificado
- Basis indicativo ajustado por risco de safra (yield_risk)
- Lei da convergência (basis tende a fechar spread vs futuro)
- Cruzamento com contango/backwardation para briefing RAG
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional


CommodityCode = Literal["soja", "milho", "boi"]


class CurveShape(str, Enum):
    """Formato da curva de futuros (oferta x demanda)."""

    FLAT = "flat"
    CONTANGO = "contango"
    BACKWARDATION = "backwardation"


class HedgeStance(str, Enum):
    """Recomendações educacionais — não são ordens de investimento."""

    MONITOR_SHORT_BASIS = "monitor_short_basis"
    MONITOR_LONG_BASIS = "monitor_long_basis"
    HEDGE_BASIS_MISMATCH_RISK = "hedge_basis_mismatch_risk"
    ESG_BLOCK = "esg_block"
    NEUTRAL = "neutral"


@dataclass
class MarketSnapshot:
    """Cotações e parâmetros de mercado para uma data de análise."""

    saca_rs: float
    tx_cambio: float
    cbot_cents_per_bu: Optional[float] = None  # soja/trigo referência CBOT
    b3_futures_rs: Optional[float] = None  # CCM milho, BGI boi, SJC soja local
    premio_exportacao_usd_t: float = 0.0
    frete_origem_rs: float = 0.0
    fobbings_usd_t: float = 0.0


@dataclass
class YieldContext:
    """Contexto agronômico (satélite + IoT) para basis indicativo."""

    yield_risk_score: int  # 0-100
    ndvi_mean: Optional[float] = None
    soil_moisture_pct: Optional[float] = None
    esg_compliant: bool = True
    esg_message: str = ""


@dataclass
class BasisResult:
    commodity: CommodityCode
    basis_atual: float
    basis_indicativo: float
    basis_unit: str
    flat_fob_usd_t: Optional[float]
    ppe_hint_rs_saca: Optional[float]
    curve_shape: CurveShape
    convergence_gap: float
    hedge_stance: HedgeStance
    narrative_hooks: list[str] = field(default_factory=list)


# --- Fórmulas do material FMDAT27 ---


def basis_soja_cbot(
    saca_rs: float,
    tx_cambio: float,
    cbot_cents_per_bu: float,
) -> float:
    """
    Basis soja/trigo vs CBOT (%):
    ((Saca R$ / Tx) / 2,204 - (CBOT/100)) * 100
    """
    if tx_cambio <= 0:
        raise ValueError("Taxa de câmbio deve ser positiva.")
    usd_per_saca = saca_rs / tx_cambio
    usd_per_bu = cbot_cents_per_bu / 100.0
    return ((usd_per_saca / 2.204) - usd_per_bu) * 100.0


def basis_milho_domestico(saca_rs: float, ccm_b3_rs: float) -> float:
    """Basis milho: (Saca R$) - (CCM B3)."""
    return saca_rs - ccm_b3_rs


def basis_boi_domestico(arroba_rs: float, bgi_b3_rs: float) -> float:
    """Basis boi gordo: (@ R$) - (BGI B3)."""
    return arroba_rs - bgi_b3_rs


def flat_fob_usd(
    contrato_futuro_usd_t: float,
    premio_exportacao_usd_t: float,
) -> float:
    """Flat Price FOB = Contrato Futuro + Prêmio de Exportação."""
    return contrato_futuro_usd_t + premio_exportacao_usd_t


def ppe_origem_rs_saca(
    flat_fob_usd_t: float,
    tx_cambio: float,
    fobbings_usd_t: float,
    frete_nacional_rs: float,
    kg_per_saca: float = 60.0,
) -> float:
    """
    PPE simplificado: deduz fobbings e frete do FOB para preço na origem (R$/saca).

    Conversão aproximada USD/t -> R$/saca para POC.
    """
    usd_per_saca = (flat_fob_usd_t - fobbings_usd_t) * (kg_per_saca / 1000.0)
    rs_at_port = usd_per_saca * tx_cambio
    return rs_at_port - frete_nacional_rs


def infer_curve_shape(futures_prices: list[float]) -> CurveShape:
    """
    Infere contango / backwardation a partir de cotações por vencimento (ordem cronológica).

    Contango: contratos longos mais caros (muita oferta / pouca demanda).
    Backwardation: curto mais caro (pouca oferta / muita demanda).
    """
    if len(futures_prices) < 2:
        return CurveShape.FLAT

    short_p, long_p = futures_prices[0], futures_prices[-1]
    spread = long_p - short_p
    threshold = abs(short_p) * 0.005

    if abs(spread) <= threshold:
        return CurveShape.FLAT
    if spread > 0:
        return CurveShape.CONTANGO
    return CurveShape.BACKWARDATION


def adjust_basis_indicativo(
    basis_atual: float,
    yield_risk_score: int,
    curve_shape: CurveShape,
) -> float:
    """
    Basis indicativo: aplica choque de oferta regional + convergência parcial.

    Quebra de safra (alto yield_risk) -> basis tende a ágio (valorizar físico local).
    Lei da convergência: indicativo puxa 30% em direção à média de longo prazo (0).
    """
    risk = max(0, min(100, yield_risk_score))
    # Ágio esperado em pontos de basis (heurística POC)
    supply_shock = (risk / 100.0) * 4.0
    if curve_shape == CurveShape.BACKWARDATION:
        supply_shock += 1.0
    elif curve_shape == CurveShape.CONTANGO:
        supply_shock -= 0.5

    raw_indicative = basis_atual + supply_shock
    # Convergência: 30% do gap vs referência neutra (0) fecha no horizonte do briefing
    convergence_target = 0.0
    return round(raw_indicative * 0.7 + convergence_target * 0.3, 4)


def convergence_gap(basis_atual: float, basis_indicativo: float) -> float:
    """Distância entre basis atual e indicativo (monitoramento da convergência)."""
    return round(basis_indicativo - basis_atual, 4)


def recommend_hedge_stance(
    basis_atual: float,
    basis_indicativo: float,
    yield_risk_score: int,
    curve_shape: CurveShape,
    esg_compliant: bool,
) -> tuple[HedgeStance, list[str]]:
    """
    Mecanismo de alinhamento basis x hedge (educacional).

    - Oferta local cai + basis em ágio -> risco de hedge na tela descasar do físico.
    - ESG fail -> bloqueio de originação.
    """
    hooks: list[str] = []
    if not esg_compliant:
        hooks.append(
            "Propriedade inelegível para originação e travamento de hedge "
            "devido a inconformidade ESG."
        )
        return HedgeStance.ESG_BLOCK, hooks

    gap = basis_indicativo - basis_atual
    risk = yield_risk_score

    if risk >= 60 and gap > 1.5:
        hooks.append(
            "Safra regional em risco: basis físico tende a ágio (Teoria da Convergência)."
        )
        hooks.append(
            "Atenção ao risco de base: hedge em contrato padronizado B3 pode ficar "
            "descasado do prêmio regional se o prêmio de risco local não for modelado."
        )
        if curve_shape == CurveShape.BACKWARDATION:
            hooks.append("Curva em backwardation reforça restrição de oferta.")
        return HedgeStance.HEDGE_BASIS_MISMATCH_RISK, hooks

    if basis_atual > 2.0:
        hooks.append("Basis em ágio: cenário educacional para monitorar Short Basis (venda do físico).")
        return HedgeStance.MONITOR_SHORT_BASIS, hooks

    if basis_atual < -2.0:
        hooks.append("Basis em deságio: cenário educacional para monitorar Long Basis (reter físico).")
        return HedgeStance.MONITOR_LONG_BASIS, hooks

    hooks.append("Basis próximo da paridade com futuro; monitorar convergência.")
    return HedgeStance.NEUTRAL, hooks


def analyze_soja(
    market: MarketSnapshot,
    yield_ctx: YieldContext,
    futures_curve: list[float],
    contrato_futuro_usd_t: float = 400.0,
) -> BasisResult:
    """Análise completa para soja (SJC / CBOT)."""
    if not yield_ctx.esg_compliant:
        return BasisResult(
            commodity="soja",
            basis_atual=0.0,
            basis_indicativo=0.0,
            basis_unit="pontos_basis_pct",
            flat_fob_usd_t=None,
            ppe_hint_rs_saca=None,
            curve_shape=CurveShape.FLAT,
            convergence_gap=0.0,
            hedge_stance=HedgeStance.ESG_BLOCK,
            narrative_hooks=[yield_ctx.esg_message or "Inconformidade ESG detectada."],
        )

    if market.cbot_cents_per_bu is None:
        raise ValueError("CBOT cents/bu obrigatório para basis de soja.")

    basis_atual = basis_soja_cbot(
        market.saca_rs,
        market.tx_cambio,
        market.cbot_cents_per_bu,
    )
    curve = infer_curve_shape(futures_curve)
    basis_ind = adjust_basis_indicativo(basis_atual, yield_ctx.yield_risk_score, curve)
    gap = convergence_gap(basis_atual, basis_ind)
    stance, hooks = recommend_hedge_stance(
        basis_atual, basis_ind, yield_ctx.yield_risk_score, curve, yield_ctx.esg_compliant
    )

    flat = flat_fob_usd(contrato_futuro_usd_t, market.premio_exportacao_usd_t)
    ppe = ppe_origem_rs_saca(
        flat,
        market.tx_cambio,
        market.fobbings_usd_t,
        market.frete_origem_rs,
    )

    return BasisResult(
        commodity="soja",
        basis_atual=round(basis_atual, 4),
        basis_indicativo=basis_ind,
        basis_unit="pontos_basis_pct",
        flat_fob_usd_t=round(flat, 2),
        ppe_hint_rs_saca=round(ppe, 2),
        curve_shape=curve,
        convergence_gap=gap,
        hedge_stance=stance,
        narrative_hooks=hooks,
    )


def analyze_milho(
    market: MarketSnapshot,
    yield_ctx: YieldContext,
    futures_curve: list[float],
) -> BasisResult:
    """Análise para milho doméstico (CCM B3)."""
    if market.b3_futures_rs is None:
        raise ValueError("Cotação CCM B3 obrigatória para milho.")

    if not yield_ctx.esg_compliant:
        return BasisResult(
            commodity="milho",
            basis_atual=0.0,
            basis_indicativo=0.0,
            basis_unit="R$/saca",
            flat_fob_usd_t=None,
            ppe_hint_rs_saca=None,
            curve_shape=CurveShape.FLAT,
            convergence_gap=0.0,
            hedge_stance=HedgeStance.ESG_BLOCK,
            narrative_hooks=[yield_ctx.esg_message or "Inconformidade ESG."],
        )

    basis_atual = basis_milho_domestico(market.saca_rs, market.b3_futures_rs)
    curve = infer_curve_shape(futures_curve)
    basis_ind = adjust_basis_indicativo(basis_atual, yield_ctx.yield_risk_score, curve)
    gap = convergence_gap(basis_atual, basis_ind)
    stance, hooks = recommend_hedge_stance(
        basis_atual, basis_ind, yield_ctx.yield_risk_score, curve, yield_ctx.esg_compliant
    )

    return BasisResult(
        commodity="milho",
        basis_atual=round(basis_atual, 4),
        basis_indicativo=basis_ind,
        basis_unit="R$/saca",
        flat_fob_usd_t=None,
        ppe_hint_rs_saca=None,
        curve_shape=curve,
        convergence_gap=gap,
        hedge_stance=stance,
        narrative_hooks=hooks,
    )


def to_rag_context(result: BasisResult, yield_ctx: YieldContext) -> dict:
    """Payload estruturado para o prompt RAG (mecanismo de alinhamento do basis)."""
    return {
        "commodity": result.commodity,
        "basis_atual": result.basis_atual,
        "basis_indicativo": result.basis_indicativo,
        "basis_unit": result.basis_unit,
        "curve_shape": result.curve_shape.value,
        "convergence_gap": result.convergence_gap,
        "yield_risk_score": yield_ctx.yield_risk_score,
        "ndvi_mean": yield_ctx.ndvi_mean,
        "soil_moisture_pct": yield_ctx.soil_moisture_pct,
        "hedge_stance": result.hedge_stance.value,
        "narrative_hooks": result.narrative_hooks,
        "flat_fob_usd_t": result.flat_fob_usd_t,
        "ppe_hint_rs_saca": result.ppe_hint_rs_saca,
        "esg_compliant": yield_ctx.esg_compliant,
    }
