from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.market_data.b3_client import B3Client
from src.market_data.ptax_client import PtaxClient, PtaxQuote


def test_ptax_csv_fallback():
    client = PtaxClient()
    with patch.object(client, "_fetch_bcb_odata", side_effect=ValueError("offline")):
        with patch.object(client, "_fetch_bcb_html_scrape", side_effect=ValueError("offline")):
            quote = client.get_ptax()
    assert quote.fonte in ("fallback_synthetic", "csv_fallback")
    assert quote.media > 4.0


def test_b3_csv_fallback():
    client = B3Client()
    with patch.object(client, "_scrape_b3_adjustments", side_effect=ValueError("offline")):
        quote = client.get_sjc_quote()
    assert quote.settlement_cents_bu > 1000
    assert len(quote.curve) == 3


def test_analysis_to_dict_roundtrip():
    from src.core_logic.orchestrator import OrbitalOrchestrator, analysis_to_dict

    analysis = OrbitalOrchestrator().run(esg_red_flag_demo=False)
    payload = analysis_to_dict(analysis)
    assert "ndvi_overlay_png_b64" in payload
    assert payload["basis"]["basis_atual"] is not None
    assert payload["briefing_markdown"]
