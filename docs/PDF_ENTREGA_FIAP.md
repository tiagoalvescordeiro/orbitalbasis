# OrbitalBasis — Documento de Entrega (esqueleto para PDF único)

**Global Solution FIAP 2026.1 · A Nova Economia Espacial**  
**Curso:** Inteligência Artificial — 2º ano  
**Grupo:** OrbitalBasis Team

> **Para colar no Word sem Markdown:** use **`PDF_ENTREGA_FIAP_COPIAR_WORD.txt`** (Ctrl+A → Ctrl+C → Word).  
> **Instruções de exportação:** `INSTRUCOES_EXPORTAR_PDF.md`  
> **Código:** fonte monoespaçada (Consolas/Courier 9–10 pt). **Não** use screenshots de código.

---

## PÁGINA 1 — IDENTIFICAÇÃO (obrigatória)

**OrbitalBasis Team. QUERO CONCORRER.**

| Integrante | RM | E-mail |
|------------|-----|--------|
| Tiago Alves Cordeiro | 561791 | 561791@fiap.com.br |
| Leandro Arthur Marinho Ferreira | 565240 | 565240@fiap.com.br |
| Otavio Custodio de Oliveira | 565606 | 565606@fiap.com.br |
| Matheus José Parra | 561907 | 561907@fiap.com.br |

**Título do projeto:** OrbitalBasis — Copiloto Orbital de Comercialização Agrícola  
**Disciplina / entrega:** Global Solution 2026.1 — Prova de Conceito (POC) e MVP funcional

---

## 1. INTRODUÇÃO

O agronegócio brasileiro opera com informações fragmentadas: o produtor enxerga clima e solo; a mesa de operações enxerga basis, curva de futuros e câmbio. Poucas ferramentas unem **dados orbitais** (satélite), **telemetria de borda** (IoT) e **indicadores financeiros** em um fluxo único de decisão com governança ESG.

O **OrbitalBasis** é uma POC/MVP que demonstra essa integração para cooperativas e mesas de commodities: processamento de NDVI por visão computacional, predição de risco de safra por Machine Learning, motor de basis/PPE com dados de mercado (PTAX BCB e B3), compliance ESG automatizado (Red Flag em APP) e copiloto comercial com RAG (ChromaDB + LangChain).

**Escopo da POC:** ambiente de demonstração com bandas sintéticas e datasets de fallback; métricas de ML obtidas sobre labels heurísticos gerados pelo próprio pipeline (transparência acadêmica). Material **educacional** — não constitui recomendação de investimento.

**Objetivo da entrega:** comprovar aplicação de IA, automação e computação à Nova Economia Espacial, conforme eixo da Global Solution 2026.1.

---

## 2. DESENVOLVIMENTO

### 2.1 Arquitetura geral

Três camadas integradas pelo `OrbitalOrchestrator`:

1. **Órbita** — bandas Red/NIR → NDVI matricial e segmentação (OpenCV/NumPy).  
2. **Campo** — ESP32 com filtragem na borda (transmissão apenas em anomalia ou janela horária).  
3. **Mercado** — PTAX, cotação soja B3, curva de futuros, basis atual vs indicativo, briefing RAG.

Camada distribuída: **FastAPI** (`/api/v1/analysis`, `/api/v1/hardware/telemetry`) e **Streamlit** (dashboard de demo para vídeo e avaliação).

### 2.2 Visão computacional — NDVI orbital

O NDVI não é consumido pronto; é calculado pixel a pixel:

```python
def compute_ndvi_matrix(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """NDVI = (NIR - Red) / (NIR + Red)."""
    red_f = red.astype(np.float32)
    nir_f = nir.astype(np.float32)
    denom = nir_f + red_f
    denom = np.where(denom == 0, np.nan, denom)
    return (nir_f - red_f) / denom
```

A segmentação triclass (saudável / atenção / estresse severo) alimenta o resumo do talhão (`ndvi_mean`, percentuais de estresse) exibido no dashboard.

**Decisão arquitetural:** manter processamento local (edge/orquestrador) para reduzir dependência de APIs externas na demo FIAP.

### 2.3 Machine Learning — risco de safra

Modelo: **RandomForestRegressor** (120 estimadores), alvo `yield_risk_score` (0–100).

Features: `ndvi_mean`, `ndvi_std`, `stress_pct_severe`, `stress_pct_attention`, `stress_pct_healthy`, `soil_moisture_pct`.

Pipeline reproduzível:

```bash
python scripts/generate_training_dataset.py --rows 8000
python scripts/train_yield_risk.py
```

Métricas versionadas (`models/yield_risk_v1_metrics.json`):

- **MAE:** 0,024  
- **R²:** 0,9999  
- **Amostras:** 8.000 (treino 6.400 / teste 1.600)

Integração em produção da POC:

```python
def ml_enabled() -> bool:
    if os.getenv("ORBITAL_USE_ML_YIELD_RISK", "true").lower() == "false":
        return False
    return DEFAULT_MODEL_PATH.exists()
```

Treino alternativo gratuito documentado em Google Colab (`notebooks/train_yield_risk_colab.ipynb`).

**Nota de compliance técnico:** R² elevado reflete dataset sintético alinhado à heurística de geração; em produção real seria necessário rotular com dados de safra observados.

### 2.4 Motor de mercado — basis, curva e convergência

O `SojaBasisEngine` calcula basis atual (CBOT + PTAX + preço físico), basis indicativo ajustado pelo risco de safra e lacuna de convergência. A curva de futuros classifica contango/backwardation.

### 2.5 Governança ESG automatizada

Cruzamento talhão × APP (Área de Preservação Permanente). Em violação simulada (`esg_red_flag`), o motor bloqueia originação:

```python
if not yield_ctx.esg_compliant:
    return BasisResult(
        commodity="soja",
        basis_atual=0.0,
        basis_indicativo=0.0,
        hedge_stance=HedgeStance.ESG_BLOCK,
        narrative_hooks=[yield_ctx.esg_message or "Inconformidade ESG detectada."],
    )
```

No dashboard: checkbox **“Simular Cenário de Risco ESG (Bandeira Vermelha)”** dispara banner RED FLAG e zeragem de basis.

### 2.6 Automação, IoT e RAG

- **ESP32** (`field_node.ino`): média móvel local; transmissão se desvio ≥ 15% ou janela horária.  
- **RAG:** base `data/rag/knowledge/` indexada em ChromaDB; modos `deterministic`, `hybrid`, `llm` via `ORBITAL_RAG_MODE`.  
- **Testes:** `pytest` — 25 testes automatizados (NDVI, basis, ML, RAG, mercado).

### 2.7 Integração das disciplinas — Fases 3 e 4 (FIAP)

| Disciplina / eixo | Evidência no OrbitalBasis |
|-------------------|---------------------------|
| Visão computacional | NDVI matricial + limiarização OpenCV |
| Machine Learning | Random Forest + métricas MAE/R² + `yield_risk_predictor.py` |
| IA generativa | RAG ChromaDB + LangChain (briefing comercial) |
| IoT / Edge computing | Firmware ESP32 com filtro de banda |
| Aplicações distribuídas | FastAPI + Streamlit consumindo `/api/v1/analysis` |
| Web scraping / APIs | PTAX BCB OData + B3 com fallback CSV |

### 2.8 Como executar (reprodutibilidade)

```bash
cd orbitalbasis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -q
uvicorn src.applications.api.main:app --reload --port 8000
streamlit run src/applications/dashboard/app.py
```

API: http://127.0.0.1:8000/docs — Dashboard: http://127.0.0.1:8501

---

## 3. RESULTADOS ESPERADOS

Ao executar a POC, o avaliador deve observar:

1. **Dashboard funcional** com split Campo (NDVI + risco safra) e Mercado (curva + basis).  
2. **Risco de safra** numérico (ex.: 64/100) com ML ativo na sidebar.  
3. **ESG OK** no cenário padrão; **RED FLAG** ao simular violação APP, com basis bloqueado.  
4. **API REST** retornando JSON com `ndvi_summary`, `esg`, `basis`, `briefing_markdown`.  
5. **Métricas ML** reproduzíveis (MAE 0,024; R² 0,9999) via scripts ou Colab.

**Resultado de negócio (demo):** visão unificada órbita → campo → mercado para apoiar conversa entre produtor e mesa (material educacional, sem promessa de rentabilidade).

*[Opcional: inserir UMA figura do dashboard aqui — captura de tela apenas para resultados visuais, não para código.]*

---

## 4. CONCLUSÕES

O OrbitalBasis cumpre o escopo da Global Solution 2026.1 ao aplicar IA e automação à Nova Economia Espacial: dados orbitais processados localmente, telemetria filtrada na borda, ML para risco de safra, governança ESG com bloqueio automatizado e camada distribuída (API + dashboard) demonstrável em até 5 minutos de vídeo.

**Limitações declaradas:** dados sintéticos/fallback em PTAX-B3 e bandas demo; labels de ML derivados de heurística; APP em máscara retangular para POC.

**Trabalhos futuros:** integração Sentinel real, GeoJSON/APP com geopandas, rotulagem de safra com dados agronômicos reais, deploy cloud com observabilidade.

**Frase de encerramento:**  
OrbitalBasis: da órbita ao campo, do campo ao mercado. **OrbitalBasis Team. QUERO CONCORRER.**

---

## 5. LINKS DE ENTREGA (obrigatório — última página)

| Item | URL |
|------|-----|
| Repositório GitHub | https://github.com/tiagoalvescordeiro/orbitalbasis |
| Vídeo demonstrativo (YouTube, **não listado**) | _[INSERIR URL APÓS GRAVAÇÃO]_ |
| Documentação complementar | https://github.com/tiagoalvescordeiro/orbitalbasis/blob/main/docs/ARQUITETURA.md |

---

## Checklist antes de enviar o PDF

- [ ] Frase **"OrbitalBasis Team. QUERO CONCORRER."** na primeira página  
- [ ] Quatro nomes **completos** + RMs  
- [ ] Seções 1–4 presentes  
- [ ] Todo código em **texto** (não imagem)  
- [ ] Link GitHub + link YouTube preenchidos  
- [ ] Aviso educacional / não recomendação de investimento  
- [ ] Arquivo único `.pdf` (não ZIP com vários PDFs)
