"""
Cliente PTAX — câmbio comercial USD/BRL (Banco Central do Brasil).

Ordem de tentativa:
1. API OData oficial BCB (REST estruturado)
2. Web scraping de página pública de cotação (fallback)
3. CSV local data/synthetic/ptax_history.csv
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FALLBACK_CSV = PROJECT_ROOT / "data" / "synthetic" / "ptax_history.csv"

BCB_PTAX_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarDia(dataCotacao=@dataCotacao)"
)
BCB_HTML_FALLBACK = "https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes"


@dataclass(frozen=True)
class PtaxQuote:
    """Cotação PTAX do dia (média compra/venda)."""

    cotacao_compra: float
    cotacao_venda: float
    data_cotacao: str
    fonte: str

    @property
    def media(self) -> float:
        return round((self.cotacao_compra + self.cotacao_venda) / 2.0, 4)


class PtaxClient:
    """Captura PTAX com fallback em camadas."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        fallback_csv: Path = FALLBACK_CSV,
        timeout_sec: int = 12,
    ) -> None:
        self._session = session or requests.Session()
        self._session.headers.update(
            {"User-Agent": "OrbitalBasis-FIAP/1.0 (Global Solution 2026.1)"}
        )
        self._fallback_csv = fallback_csv
        self._timeout = timeout_sec

    def get_ptax(self, reference_date: Optional[date] = None) -> PtaxQuote:
        ref = reference_date or date.today()
        for attempt_date in _business_days_back(ref, max_days=14):
            try:
                quote = self._fetch_bcb_odata(attempt_date)
                logger.info("PTAX via BCB OData: %s = %.4f", quote.data_cotacao, quote.media)
                return quote
            except Exception as exc:
                logger.warning("BCB OData falhou para %s: %s", attempt_date, exc)

        try:
            quote = self._fetch_bcb_html_scrape(ref)
            logger.info("PTAX via scraping BCB: %.4f", quote.media)
            return quote
        except Exception as exc:
            logger.warning("Scraping BCB falhou: %s", exc)

        quote = self._load_csv_fallback()
        logger.warning("PTAX via CSV fallback: %.4f (%s)", quote.media, quote.fonte)
        return quote

    def _fetch_bcb_odata(self, ref: date) -> PtaxQuote:
        date_param = ref.strftime("%m-%d-%Y")
        url = f"{BCB_PTAX_URL}?@dataCotacao='{date_param}'&$format=json"
        resp = self._session.get(url, timeout=self._timeout)
        resp.raise_for_status()
        payload = resp.json()
        rows = payload.get("value") or []
        if not rows:
            raise ValueError(f"Sem cotação PTAX para {date_param}")

        row = rows[0]
        compra = float(row["cotacaoCompra"])
        venda = float(row["cotacaoVenda"])
        return PtaxQuote(
            cotacao_compra=compra,
            cotacao_venda=venda,
            data_cotacao=row.get("dataHoraCotacao", date_param)[:10],
            fonte="bcb_odata",
        )

    def _fetch_bcb_html_scrape(self, ref: date) -> PtaxQuote:
        """Fallback: tenta extrair referência numérica de página institucional."""
        resp = self._session.get(BCB_HTML_FALLBACK, timeout=self._timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        # Heurística: último valor no formato X,XXXX próximo de faixa PTAX recente
        import re

        matches = re.findall(r"\b([4-6]),(\d{4})\b", text)
        if not matches:
            raise ValueError("Nenhum valor PTAX encontrado no HTML do BCB")
        inteiro, frac = matches[-1]
        value = float(f"{inteiro}.{frac}")
        return PtaxQuote(
            cotacao_compra=value,
            cotacao_venda=value,
            data_cotacao=ref.isoformat(),
            fonte="bcb_html_scrape",
        )

    def _load_csv_fallback(self) -> PtaxQuote:
        if not self._fallback_csv.exists():
            raise FileNotFoundError(f"CSV fallback ausente: {self._fallback_csv}")

        with open(self._fallback_csv, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            raise ValueError("CSV PTAX vazio")

        row = rows[-1]
        compra = float(row["cotacao_compra"])
        venda = float(row["cotacao_venda"])
        return PtaxQuote(
            cotacao_compra=compra,
            cotacao_venda=venda,
            data_cotacao=row.get("date", datetime.now().date().isoformat()),
            fonte=row.get("fonte", "csv_fallback"),
        )


def _business_days_back(start: date, max_days: int) -> list[date]:
    out: list[date] = []
    current = start
    for _ in range(max_days):
        if current.weekday() < 5:
            out.append(current)
        current -= timedelta(days=1)
    return out


def get_ptax_quote(reference_date: Optional[date] = None) -> PtaxQuote:
    """Atalho funcional para uso no orchestrator."""
    return PtaxClient().get_ptax(reference_date)
