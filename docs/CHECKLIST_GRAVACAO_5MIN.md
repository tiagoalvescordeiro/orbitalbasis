# Checklist cronometrada — Vídeo FIAP (máx. 5 minutos)

**Grupo:** OrbitalBasis Team · RMs 561791, 565240, 565606, 561907  
**Alvo:** YouTube **Não listado** · 1080p · áudio limpo

---

## Antes de gravar (15 min)

| # | Ação | OK |
|---|------|-----|
| 1 | API rodando: `uvicorn src.applications.api.main:app --reload --port 8000` | [ ] |
| 2 | Dashboard: `streamlit run src/applications/dashboard/app.py` → http://127.0.0.1:8501 | [ ] |
| 3 | Testar checkbox **ESG Red Flag** uma vez (saber onde fica) | [ ] |
| 4 | Testar **Atualizar análise** com preço ~115 e umidade ~22% | [ ] |
| 5 | (Opcional) Aba Colab com MAE/R² visível ou terminal com `cat models/yield_risk_v1_metrics.json` | [ ] |
| 6 | Fechar abas/notificações; desativar tradução automática do Chrome no localhost | [ ] |
| 7 | Roteiro impresso ou em segundo monitor: `docs/ROTEIRO_DO_VIDEO.md` | [ ] |

---

## Cronômetro — 5:00 total

### 0:00 – 0:15 | ABERTURA OBRIGATÓRIA

**Tela:** rosto do grupo OU slide com logo + nomes.

**Falar (literal):**

> **"OrbitalBasis Team. QUERO CONCORRER."**

> "Somos o grupo OrbitalBasis Team, RM 561791, 565240, 565606 e 561907. Apresentamos o OrbitalBasis — copiloto que une satélite, sensores de campo e mercado de commodities."

| OK |
|----|
| [ ] Frase exata nos primeiros 15 s |
| [ ] RMs citados |

---

### 0:15 – 1:00 | PROBLEMA

**Tela:** dashboard vazio → preencher com **Atualizar análise**.

**Falar (~45 s):**

> "No agro, produtor vê clima; a mesa vê basis. O OrbitalBasis conecta os dois: NDVI, umidade, PTAX, B3, ESG e briefing em um só lugar."

| OK |
|----|
| [ ] Dashboard visível |
| [ ] Botão atualizar clicado |

---

### 1:00 – 2:00 | ÓRBITA + VISÃO COMPUTACIONAL

**Tela:** coluna esquerda — mapa NDVI colorido + métricas.

**Falar (~60 s):**

> "Calculamos NDVI na matriz: NIR menos Red, dividido pela soma. OpenCV classifica verde, amarelo e vermelho. Isso gera o risco de safra que ajusta o basis."

**Mostrar:** NDVI médio, estresse severo, **Risco safra X/100**.

| OK |
|----|
| [ ] Mapa segmentado na tela |
| [ ] Risco safra legível |

---

### 2:00 – 2:45 | IoT / EDGE

**Tela:** sidebar — umidade manual + texto ESP32; ou foto/Wokwi do ESP32.

**Falar (~45 s):**

> "Na economia espacial, banda é cara. O ESP32 filtra na borda: só transmite se umidade desviar quinze por cento da média ou na janela horária."

| OK |
|----|
| [ ] Menção a edge/banda |
| [ ] Umidade na sidebar visível |

---

### 2:45 – 3:30 | MERCADO

**Tela:** coluna direita — curva de futuros + gráfico basis atual vs indicativo.

**Falar (~45 s):**

> "PTAX via Banco Central, soja na B3. A curva mostra contango ou backwardation. Abaixo, basis atual versus indicativo — teoria da convergência."

| OK |
|----|
| [ ] Dois gráficos Plotly visíveis |
| [ ] Valores de basis legíveis |

---

### 3:30 – 4:15 | ESG + RAG (obrigatório para pódio)

**Tela:** marcar **Simular Cenário de Risco ESG** → **Atualizar análise**.

**Falar (~30 s):**

> "Com Red Flag ESG, a propriedade fica inelegível: basis bloqueado, sem originação."

**Tela:** desmarcar ESG → briefing normal.

**Falar (~15 s):**

> "O copiloto RAG consulta nossa base e gera briefing educacional — sem promessa de rentabilidade."

| OK |
|----|
| [ ] Banner RED FLAG apareceu |
| [ ] ESG OK restaurado |
| [ ] Menção RAG/briefing |

---

### 4:15 – 4:45 | ML + ARQUITETURA DISTRIBUÍDA

**Tela:** sidebar "ML risco safra ativo" OU Colab/terminal com métricas **MAE 0,024 · R² 0,9999**.

**Falar (~30 s):**

> "Treinamos Random Forest para risco de safra. FastAPI expõe a análise; Streamlit é o dashboard. Integração das fases 3 e 4: visão, ML, apps distribuídas e IoT."

| OK |
|----|
| [ ] ML ou métricas na tela |
| [ ] FastAPI + Streamlit citados |

---

### 4:45 – 5:00 | ENCERRAMENTO

**Tela:** slide final com QR GitHub ou README.

**Falar (literal):**

> "OrbitalBasis: da órbita ao campo, do campo ao mercado. **OrbitalBasis Team. QUERO CONCORRER.** Obrigado."

| OK |
|----|
| [ ] Frase de pódio repetida no final |
| [ ] Vídeo ≤ 5:00 (cortar se passar) |

---

## Depois de gravar (10 min)

| # | Ação | OK |
|---|------|-----|
| 1 | Upload YouTube → visibilidade **Não listado** | [ ] |
| 2 | Colar URL no `README.md` (seção Entrega FIAP) | [ ] |
| 3 | Colar URL na última página do PDF | [ ] |
| 4 | Exportar PDF a partir de `docs/PDF_ENTREGA_FIAP.md` | [ ] |
| 5 | Enviar pelo portal FIAP conforme edital | [ ] |
| 6 | `git push` com README atualizado (se alterou) | [ ] |

---

## Frases proibidas (compliance)

- Não prometer rentabilidade ou "lucro garantido".  
- Não dar consultoria fiscal/jurídica definitiva.  
- Usar: *"material educacional"*, *"POC"*, *"demonstração"*.

---

## Links rápidos

- Dashboard: http://127.0.0.1:8501  
- API docs: http://127.0.0.1:8000/docs  
- Repositório: https://github.com/tiagoalvescordeiro/orbitalbasis  
- Roteiro completo: `docs/ROTEIRO_DO_VIDEO.md`  
- Esqueleto PDF: `docs/PDF_ENTREGA_FIAP.md`
