# Checklist — Entrega final FIAP 2026.1

**Grupo:** OrbitalBasis Team · RMs 561791, 565240, 565606, 561907

---

## Repositório GitHub

- [x] Código MVP (ML, NDVI, ESG, API, dashboard, RAG, ESP32)
- [x] README alinhado ao template (integrantes, execução, pódio)
- [x] 25 testes pytest passando
- [ ] E-mails institucionais confirmados no README e PDF
- [ ] Tutor e Coordenador preenchidos no README
- [ ] `git push` com modelo ML e documentação atualizados
- [ ] Link do vídeo no README (seção Links)

---

## PDF único

- [ ] Abrir `PDF_ENTREGA_FIAP_COPIAR_WORD.txt` → colar no Word
- [ ] Página 1: **OrbitalBasis Team. QUERO CONCORRER.** + 4 nomes + e-mails
- [ ] Seções: Introdução, Desenvolvimento, Resultados, Conclusões, Links
- [ ] Código em texto (Consolas) — **sem screenshot de código**
- [ ] Inserir diagrama (de `ARQUITETURA.md`) e 1 print do dashboard
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
