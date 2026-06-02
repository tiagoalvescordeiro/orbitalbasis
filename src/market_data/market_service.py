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
        market = MarketSnapshot(
            saca_rs=self._saca_rs,
            tx_cambio=ptax.media,
            cbot_cents_per_bu=b3.settlement_cents_bu,
            premio_exportacao_usd_t=ANCORD_PREMIO_FOB_USD_T,
            frete_origem_rs=ANCORD_FRETE_ORIGEM_RS_SACA,
            fobbings_usd_t=ANCORD_FOBBINGS_USD_T,
        )
        meta = {
            "ptax_fonte": ptax.fonte,
            "ptax_data": ptax.data_cotacao,
            "b3_fonte": b3.fonte,
            "b3_contract": b3.contract_code,
            "b3_data": b3.data_ref,
            "logistics_source": "ancord_agro_100",
        }
        logger.info("MarketSnapshot montado: PTAX=%.4f B3=%.2f", ptax.media, b3.settlement_cents_bu)
        return market, b3.curve, meta
