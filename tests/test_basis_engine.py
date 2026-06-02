from src.core_logic.basis_engine import (
    CurveShape,
    HedgeStance,
    MarketSnapshot,
    YieldContext,
    adjust_basis_indicativo,
    analyze_soja,
    basis_soja_cbot,
    infer_curve_shape,
)


def test_basis_soja_formula():
    # Valores ilustrativos; valida apenas estrutura da fórmula
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
