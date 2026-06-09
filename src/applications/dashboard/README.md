## Dashboard Streamlit — Painel de Controle

Interface split-screen: orbital + mercado.

### Como rodar

```bash
streamlit run src/applications/dashboard/app.py
```

### Recursos

- Coluna esquerda: NDVI matricial color-coded
- Coluna direita: Basis, curva, PPE, telemetria ESP32
- Sidebar: Checkbox "Simular Cenário de Risco ESG" + uso de telemetria ESP32
- Briefing RAG em tempo real

### Assets de demonstração

Screenshots gerados para o PDF e README:

- [`assets/dashboard_demo.png`](../../../assets/dashboard_demo.png)
- [`assets/dashboard_esg_red_flag.png`](../../../assets/dashboard_esg_red_flag.png)

Regenerar: `python scripts/generate_assets.py`
