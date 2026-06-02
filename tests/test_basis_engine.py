import pytest

from src.core_logic.basis_engine import (
    CurveShape,
    HedgeStance,
    MarketSnapshot,
    YieldContext,
    adjust_basis_indicativo,
    analyze_soja,
    basis_soja_cbot,
    cbot_cents_to_usd_per_ton,
    flat_fob_usd,
    infer_curve_shape,
    ppe_origem_rs_saca,
)
from src.core_logic.orchestrator import compute_yield_risk_score
from src.market_data.ancord_defaults import (
    ANCORD_AULA1_CAMBIO,
    ANCORD_AULA1_CBOT_CENTS,
    ANCORD_AULA2_BASIS_CENTS,
    ANCORD_AULA2_CAMBIO,
    ANCORD_AULA2_CASH_RS_SACA,
    ANCORD_AULA2_CBOT_CENTS,
    ANCORD_FOBBINGS_USD_T,
    ANCORD_FRETE_ORIGEM_RS_SACA,
    ANCORD_PPE_EX_WORKS_RS_SACA,
    ANCORD_PREMIO_FOB_USD_T,
)


def test_basis_soja_formula():
    b = basis_soja_cbot(saca_rs=140.0, tx_cambio=5.0, cbot_cents_per_bu=1000.0)
    assert isinstance(b, float)


def test_curve_contango():
    assert infer_curve_shape([100.0, 102.0, 105.0]) == CurveShape.CONTANGO


def test_curve_backwardation():
    assert infer_curve_shape([105.0, 102.0, 100.0]) == CurveShape.BACKWARDATION


def test_high_yield_risk_increases_indicative_basis():
    atual = 2.0
    ind_low = adjust_basis_indicativo(atual, yield_risk_score=10, curve_shape=CurveShape.FLAT)
    ind_high = adjust_basis_indicativo(atual, yield_risk_score=80, curve_shape=CurveShape.BACKWARDATION)
    assert ind_high > ind_low


def test_esg_block():
    market = MarketSnapshot(saca_rs=140, tx_cambio=5.0, cbot_cents_per_bu=1000)
    yield_ctx = YieldContext(yield_risk_score=50, esg_compliant=False, esg_message="ESG fail")
    result = analyze_soja(market, yield_ctx, futures_curve=[100, 101])
    assert result.hedge_stance == HedgeStance.ESG_BLOCK


def test_analyze_soja_ok():
    market = MarketSnapshot(saca_rs=142, tx_cambio=5.12, cbot_cents_per_bu=1085)
    yield_ctx = YieldContext(yield_risk_score=65, ndvi_mean=0.42, esg_compliant=True)
    result = analyze_soja(market, yield_ctx, futures_curve=[1080, 1095, 1110])
    assert result.basis_atual is not None
    assert result.hedge_stance in HedgeStance


def test_ancord_aula2_basis_regression():
    """Valida fórmula de basis contra exercício Ancord Agro 100 — Aula 2."""
    basis = basis_soja_cbot(
        ANCORD_AULA2_CASH_RS_SACA,
        ANCORD_AULA2_CAMBIO,
        ANCORD_AULA2_CBOT_CENTS,
    )
    assert basis == pytest.approx(ANCORD_AULA2_BASIS_CENTS, abs=0.01)


def test_ancord_aula1_ppe_regression():
    """PPE Ex-Works calibrado com cascata Ancord Agro 100 — Aula 1."""
    futuro_usd_t = cbot_cents_to_usd_per_ton(ANCORD_AULA1_CBOT_CENTS)
    flat = flat_fob_usd(futuro_usd_t, ANCORD_PREMIO_FOB_USD_T)
    ppe = ppe_origem_rs_saca(
        flat,
        ANCORD_AULA1_CAMBIO,
        ANCORD_FOBBINGS_USD_T,
        ANCORD_FRETE_ORIGEM_RS_SACA,
    )
    assert ppe == pytest.approx(ANCORD_PPE_EX_WORKS_RS_SACA, abs=0.5)


def test_analyze_soja_ppe_uses_cbot_conversion():
    market = MarketSnapshot(
        saca_rs=ANCORD_AULA2_CASH_RS_SACA,
        tx_cambio=ANCORD_AULA1_CAMBIO,
        cbot_cents_per_bu=ANCORD_AULA1_CBOT_CENTS,
        premio_exportacao_usd_t=ANCORD_PREMIO_FOB_USD_T,
        frete_origem_rs=ANCORD_FRETE_ORIGEM_RS_SACA,
        fobbings_usd_t=ANCORD_FOBBINGS_USD_T,
    )
    yield_ctx = YieldContext(yield_risk_score=20, esg_compliant=True)
    result = analyze_soja(market, yield_ctx, futures_curve=[1158, 1165, 1170])
    assert result.ppe_hint_rs_saca == pytest.approx(ANCORD_PPE_EX_WORKS_RS_SACA, abs=0.5)


def test_cbot_cents_to_usd_per_ton():
    usd_t = cbot_cents_to_usd_per_ton(1218.5)
    assert 440 < usd_t < 460


def test_soil_moisture_boosts_yield_risk_below_18():
    assert compute_yield_risk_score(64, 22.0) == 64
    assert compute_yield_risk_score(64, 17.0) == 72
    assert compute_yield_risk_score(96, 15.0) == 100
