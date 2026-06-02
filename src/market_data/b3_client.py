"""
Cliente cotações B3 — contrato soja SJC (referência demo Global Solution).

Ordem:
1. Scraping página pública de ajustes/preços B3 (BeautifulSoup)
2. CSV fallback data/synthetic/b3_quotes_sjc.csv
"""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FALLBACK_CSV = PROJECT_ROOT / "data" / "synthetic" / "b3_quotes_sjc.csv"

# Página de consultas B3 (estrutura pode mudar; fallback garante demo)
B3_DERIVATIVES_URL = (
    "https://www.b3.com.br/pt_br/market-data-e-indices/"
    "servicos-de-dados/market-data/consultas/mercado-de-derivativos/"
    "precos-de-ajustes/precos-de-ajustes/"
)


@dataclass(frozen=True)
class B3SoyQuote:
    """Cotação simplificada soja B3 + curva para gráfico."""

    contract_code: str
    settlement_cents_bu: float
    curve: list[float]
    data_ref: str
    fonte: str


class B3Client:
    """Captura cotações B3 com fallback robusto."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        fallback_csv: Path = FALLBACK_CSV,
        timeout_sec: int = 15,
    ) -> None:
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "OrbitalBasis-FIAP/1.0",
                "Accept-Language": "pt-BR,pt;q=0.9",
            }
        )
        self._fallback_csv = fallback_csv
        self._timeout = timeout_sec

    def get_sjc_quote(self) -> B3SoyQuote:
        try:
            quote = self._scrape_b3_adjustments()
            logger.info(
                "B3 via scraping: %s @ %.2f c/bu",
                quote.contract_code,
                quote.settlement_cents_bu,
            )
            return quote
        except Exception as exc:
            logger.warning("Scraping B3 falhou: %s", exc)

        quote = self._load_csv_fallback()
        logger.warning(
            "B3 via CSV fallback: %s @ %.2f",
            quote.contract_code,
            quote.settlement_cents_bu,
        )
        return quote

    def _scrape_b3_adjustments(self) -> B3SoyQuote:
        resp = self._session.get(B3_DERIVATIVES_URL, timeout=self._timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # Busca padrões numéricos compatíveis com centavos de dólar por bushel (soja)
        candidates = re.findall(r"\b(1[01]\d{2}|12\d{2})\b", text)
        if not candidates:
            raise ValueError("Nenhuma cotação numérica encontrada na página B3")

        settlement = float(candidates[0])
        curve = [
            round(settlement - 3.0, 2),
            round(settlement, 2),
            round(settlement + 12.0, 2),
            round(settlement + 22.0, 2),
        ]
        return B3SoyQuote(
            contract_code="SJCH26",
            settlement_cents_bu=settlement,
            curve=curve[-3:],
            data_ref=datetime.now().date().isoformat(),
            fonte="b3_scrape",
        )

    def _load_csv_fallback(self) -> B3SoyQuote:
        if not self._fallback_csv.exists():
            raise FileNotFoundError(f"CSV B3 ausente: {self._fallback_csv}")

        with open(self._fallback_csv, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            raise ValueError("CSV B3 vazio")

        row = rows[-1]
        curve = [
            float(row["curve_m1"]),
            float(row["curve_m2"]),
            float(row["curve_m3"]),
        ]
        return B3SoyQuote(
            contract_code=row.get("contract_code", "SJCH26"),
            settlement_cents_bu=float(row["settlement_cents_bu"]),
            curve=curve,
            data_ref=row.get("date", datetime.now().date().isoformat()),
            fonte=row.get("fonte", "csv_fallback"),
        )


def get_sjc_quote() -> B3SoyQuote:
    return B3Client().get_sjc_quote()
