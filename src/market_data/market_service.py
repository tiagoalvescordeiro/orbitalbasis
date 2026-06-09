"""Agrega PTAX + B3 em MarketSnapshot para o orchestrator."""

from __future__ import annotations

import logging

from src.core_logic.basis_engine import MarketSnapshot
from src.market_data.ancord_defaults import (
    ANCORD_FOBBINGS_USD_T,
    ANCORD_FRETE_ORIGEM_RS_SACA,
    ANCORD_PREMIO_FOB_USD_T,
    DEFAULT_SACA_RS,
)
from src.market_data.b3_client import B3Client
from src.market_data.ptax_client import PtaxClient

logger = logging.getLogger(__name__)


class MarketDataService:
    def __init__(
        self,
        ptax_client: PtaxClient | None = None,
        b3_client: B3Client | None = None,
        saca_rs: float = DEFAULT_SACA_RS,
    ) -> None:
        self._ptax = ptax_client or PtaxClient()
        self._b3 = b3_client or B3Client()
        self._saca_rs = saca_rs

    def build_snapshot(self) -> tuple[MarketSnapshot, list[float], dict]:
        ptax = self._ptax.get_ptax()
        b3 = self._b3.get_sjc_quote()

        cbot_cents = b3.settlement_cents_bu
        curve = b3.curve
        fonte = b3.fonte
        contract = b3.contract_code
        cattle_cents = 0.0
        cattle_history = []
        corn_cents = 0.0
        coffee_cents = 0.0
        
        try:
            import yfinance as yf
            tk = yf.Ticker("ZS=F")
            hist = tk.history(period="1mo")
            if not hist.empty:
                cbot_cents = float(hist["Close"].iloc[-1])
                curve = [round(cbot_cents - 5.0, 2), round(cbot_cents, 2), round(cbot_cents + 15.0, 2)]
                fonte = "yfinance (ZS=F realtime)"
                contract = "ZS=F"
                history_data = [{"date": str(d.date())[5:], "price": round(float(p), 2)} for d, p in zip(hist.index, hist["Close"])]
                
            tk_cattle = yf.Ticker("LE=F")
            hist_cattle = tk_cattle.history(period="1mo")
            if not hist_cattle.empty:
                cattle_cents = float(hist_cattle["Close"].iloc[-1])
                cattle_history = [{"date": str(d.date())[5:], "price": round(float(p), 2)} for d, p in zip(hist_cattle.index, hist_cattle["Close"])]
                
            tk_corn = yf.Ticker("ZC=F")
            hist_corn = tk_corn.history(period="1mo")
            corn_history = []
            if not hist_corn.empty:
                corn_cents = float(hist_corn["Close"].iloc[-1])
                corn_history = [{"date": str(d.date())[5:], "price": round(float(p), 2)} for d, p in zip(hist_corn.index, hist_corn["Close"])]
                
            tk_coffee = yf.Ticker("KC=F")
            hist_coffee = tk_coffee.history(period="1mo")
            coffee_history = []
            if not hist_coffee.empty:
                coffee_cents = float(hist_coffee["Close"].iloc[-1])
                coffee_history = [{"date": str(d.date())[5:], "price": round(float(p), 2)} for d, p in zip(hist_coffee.index, hist_coffee["Close"])]
        except Exception as e:
            logger.warning(f"yfinance failed: {e}")

        market = MarketSnapshot(
            saca_rs=self._saca_rs,
            tx_cambio=ptax.media,
            cbot_cents_per_bu=cbot_cents,
            premio_exportacao_usd_t=ANCORD_PREMIO_FOB_USD_T,
            frete_origem_rs=ANCORD_FRETE_ORIGEM_RS_SACA,
            fobbings_usd_t=ANCORD_FOBBINGS_USD_T,
        )
        meta = {
            "ptax_fonte": ptax.fonte,
            "ptax_data": ptax.data_cotacao,
            "ptax_media": ptax.media,
            "b3_fonte": fonte,
            "b3_contract": contract,
            "b3_data": b3.data_ref,
            "b3_history": history_data,
            "cattle_cents": cattle_cents,
            "cattle_history": cattle_history,
            "corn_cents": corn_cents,
            "corn_history": corn_history,
            "coffee_cents": coffee_cents,
            "coffee_history": coffee_history,
            "logistics_source": "ancord_agro_100",
        }
        logger.info("MarketSnapshot montado: PTAX=%.4f B3=%.2f", ptax.media, cbot_cents)
        return market, curve, meta
