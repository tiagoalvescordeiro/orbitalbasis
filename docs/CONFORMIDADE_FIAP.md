# Conformidade — Enunciado FIAP vs Repositório

**Global Solution 2026.1 · A Nova Economia Espacial**  
**Projeto:** OrbitalBasis · **Grupo:** OrbitalBasis Team  
**Repositório:** https://github.com/tiagoalvescordeiro/orbitalbasis

Última verificação: 09/06/2026

---

## Template oficial ([Global-Solution-2](https://github.com/CaiqueFiap-2026/TEMPLATE-TIAO-2026/tree/main/2TIAO/Global-Solution-2))

| Requisito template | Status | Evidência |
|--------------------|--------|-----------|
| Nome do grupo | OK | README — OrbitalBasis Team |
| Integrantes (nome, RM, e-mail) | OK | README + PDF |
| Tutor(a) / Coordenador(a) | Pendente | Placeholder no README — preencher |
| Descrição do projeto | OK | README + PDF seção 1 |
| Estrutura `src/`, `data/`, `docs/` | OK | Raiz do repositório |
| Links (GitHub, vídeo, decisões técnicas) | Parcial | GitHub OK; vídeo YouTube pendente |
| Como executar o código | OK | README + PDF §2.8 |
| Histórico de lançamentos | OK | README v1.0.0 |
| Licença CC BY 4.0 | OK | `LICENSE` |
| Competição / pódio | OK | "QUERO CONCORRER" no README e PDF |

---

## Eixo temático — Nova Economia Espacial

| Critério FIAP | Status | Implementação |
|---------------|--------|---------------|
| Dados orbitais / satélite | OK | `ndvi_processor.py` — NDVI matricial Red/NIR |
| Integração Terra ↔ espaço | OK | Órbita + campo (ESP32) + mercado (basis) |
| IA / automação | OK | Random Forest, RAG, ESG automatizado |
| POC/MVP demonstrável | OK | API FastAPI + dashboard Streamlit |

---

## Disciplinas — Fases 3 e 4 (IA 2º ano)

| Disciplina | Status | Módulo / artefato |
|------------|--------|-------------------|
| Visão computacional | OK | `src/ml_models/ndvi_processor.py`, OpenCV |
| Machine Learning | OK | `yield_risk_predictor.py`, MAE 0,024, R² 0,9999 |
| IA generativa (RAG) | OK | ChromaDB + LangChain, `commercial_copilot.py` |
| IoT / Edge computing | OK | `field_node.ino` — filtro 15% + janela horária |
| Aplicações distribuídas | OK | FastAPI `/api/v1/*` + Streamlit |
| Web scraping / APIs | OK | PTAX BCB OData, B3 + fallback CSV |

---

## Entregáveis documentados (PDF + vídeo)

| Item | Status | Observação |
|------|--------|------------|
| PDF único | OK | `docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf` |
| Código em texto (não screenshot) | OK | `PDF_ENTREGA_FIAP_COPIAR_WORD.txt` |
| Vídeo ≤ 5 min (YouTube não listado) | Pendente | Gravar e colar link |
| 25 testes pytest | OK | `pytest tests/ -q` → 25 passed |
| ESG Red Flag na demo | OK | Dashboard checkbox + API `esg_red_flag=true` |
| ML ativo na demo | OK | Sidebar dashboard + `models/yield_risk_v1.joblib` |

---

## Pendências do grupo (ação manual)

1. Preencher **Tutor(a)** e **Coordenador(a)** no README.
2. Confirmar **e-mails @fiap.com.br** com a turma.
3. Gravar vídeo (primeiros 15 s: *"OrbitalBasis Team. QUERO CONCORRER."*).
4. Inserir link YouTube no README, PDF e portal FIAP.
5. (Opcional) Inserir captura do dashboard no PDF antes do envio final.
