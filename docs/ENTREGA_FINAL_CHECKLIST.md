# Checklist — Entrega final FIAP 2026.1

**Grupo:** OrbitalBasis Team · RMs 561791, 565240, 565606, 561907

---

## Repositório GitHub

- [x] Código MVP (ML, NDVI, ESG, API, dashboard, RAG, ESP32)
- [x] README alinhado ao [template FIAP Global-Solution-2](https://github.com/CaiqueFiap-2026/TEMPLATE-TIAO-2026/tree/main/2TIAO/Global-Solution-2) (integrantes, execução, pódio, histórico)
- [x] Estrutura `src/`, `data/`, `docs/` + extensões `models/`, `scripts/`, `tests/`, `notebooks/`
- [x] 53 testes pytest passando
- [x] Modelo `models/yield_risk_v1.joblib` e métricas no repositório remoto
- [x] PDF `docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf` no GitHub
- [x] Docs GCP Vertex (`ML_VERTEX_GCP.md`, notebook e script) — incluir no próximo push
- [x] Licença CC BY 4.0 (`LICENSE`) + workflow CI pytest
- [x] Pasta `assets/` com dashboard, NDVI, arquitetura e IoT (`python scripts/generate_assets.py`)
- [ ] E-mails institucionais confirmados com a turma (README e PDF)
- [ ] Tutor(a) e Coordenador(a) preenchidos no README
- [ ] `git push` final após preencher vídeo e professores
- [ ] Link do vídeo no README, PDF e portal FIAP

---

## PDF único

- [x] PDF gerado: `docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf` (`python scripts/generate_entrega_pdf.py`)
- [ ] (Opcional) Abrir `PDF_ENTREGA_FIAP_COPIAR_WORD.txt` → Word se quiser personalizar + print dashboard
- [ ] Página 1: **OrbitalBasis Team. QUERO CONCORRER.** + 4 nomes + e-mails
- [ ] Seções: Introdução, Desenvolvimento, Resultados, Conclusões, Links
- [ ] Código em texto (Consolas) — **sem screenshot de código**
- [x] Diagrama (`assets/arquitetura_orbitalbasis.png`) e print dashboard (`assets/dashboard_demo.png`)
- [x] PDF regenerado com figura embutida (`python scripts/generate_entrega_pdf.py`)
- [ ] Link GitHub + YouTube na última página
- [ ] Exportar **um** arquivo `.pdf`
- [ ] Colar link do PDF no README (se hospedar no Drive) ou anexar no portal

---

## Vídeo (máx. 5 min, YouTube não listado)

- [ ] Seguir `CHECKLIST_GRAVACAO_5MIN.md`
- [ ] Primeiros 15 s: **"OrbitalBasis Team. QUERO CONCORRER."**
- [ ] Demo dashboard + ESG Red Flag + ML ativo
- [ ] Upload **Não listado**
- [ ] URL no README, PDF e portal FIAP

---

## Portal FIAP

- [ ] Enviar PDF
- [ ] Enviar link GitHub
- [ ] Enviar link YouTube
- [ ] Confirmar prazo da disciplina

---

## Comandos de validação (antes de enviar)

```powershell
cd orbitalbasis
.\.venv\Scripts\Activate.ps1
pytest tests/ -q
uvicorn src.applications.api.main:app --reload --port 8000
# outro terminal:
streamlit run src/applications/dashboard/app.py
```

Teste ESG na API:

```powershell
python -c "import requests; d=requests.post('http://127.0.0.1:8000/api/v1/analysis',json={'spot_price':200,'esg_red_flag':True}).json(); print(d['esg']['red_flag'], d['basis']['hedge_stance'])"
```

Esperado: `True esg_block`
