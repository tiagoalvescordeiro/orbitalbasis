## Módulo de Dados de Mercado — Web Scraping + APIs

Captura PTAX (BCB) e cotações B3 (soja SJC) com fallback em camadas.

### Arquivos

- `ptax_client.py` — API OData BCB → scraping → CSV fallback
- `b3_client.py` — Scraping B3 → CSV fallback
- `market_service.py` — Integra em MarketSnapshot

### Fontes

1. API OData oficial (BCB/B3)
2. Web scraping com BeautifulSoup
3. CSV sintético local

Logs indicam: `bcb_odata` | `b3_scrape` | `csv_fallback`

## Calibração Ancord Agro 100

Logística default (`premio`, `fobbings`, `frete origem`) e cash físico inicial vêm de `ancord_defaults.py` (referência educacional Aulas 1–2). PTAX e CBOT continuam ao vivo ou via CSV fallback.
