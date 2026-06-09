## Assets — Comprovação visual FIAP 2026.1

Imagens geradas para PDF, README e avaliação do MVP.

### Gerar / atualizar

```bash
python scripts/generate_assets.py
```

### Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `dashboard_demo.png` | Painel demo — cenário ESG OK + ML ativo |
| `dashboard_esg_red_flag.png` | Painel demo — RED FLAG ESG + basis bloqueado |
| `ndvi_overlay_sample.png` | Overlay NDVI (verde / amarelo / vermelho) |
| `arquitetura_orbitalbasis.png` | Diagrama órbita → campo → mercado → IA |
| `logo-fiap.png` | Logo institucional (template TIAO 2026) |
| `esp32/iot_data_flow.png` | Fluxo ESP32 → MQTT → API → Dashboard |

### Uso na entrega

- **PDF:** figura na seção Resultados (`docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf`)
- **README:** links abaixo na seção Links
- **Vídeo:** usar `dashboard_esg_red_flag.png` como referência de roteiro

### Screenshots ao vivo (opcional)

Para capturas reais do Streamlit, rode o dashboard e grave a tela:

```bash
streamlit run src/applications/dashboard/app.py
```

Substitua os PNGs acima se preferir prints reais da interface.
