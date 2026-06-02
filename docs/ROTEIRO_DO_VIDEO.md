# OrbitalBasis — Roteiro de Vídeo (5 minutos)

**Global Solution FIAP 2026.1 · A Nova Economia Espacial**  
**Curso:** Inteligência Artificial — 2º ano

> Equipe: **OrbitalBasis Team** · RMs **561791, 565240, 565606, 561907**

---

## 0:00 – 0:15 | Abertura obrigatória

**[Tela: rosto do grupo ou slide institucional]**

> **"OrbitalBasis Team. QUERO CONCORRER."**

**[Corte para dashboard OrbitalBasis]**

> "Somos o grupo OrbitalBasis Team, RM 561791, 565240, 565606, 561907. Apresentamos o **OrbitalBasis** — o copiloto que conecta dados orbitais, sensores de borda e o mercado físico de commodities agrícolas."

---

## 0:15 – 1:00 | Problema e contexto de mercado

**[Slide ou narração sobre SAG / basis]**

> "No agronegócio, o produtor enxerga o clima. A mesa de operações enxerga o basis. Quase nunca os dois conversam. Segundo a formação em derivativos agrícolas, o preço físico não é o preço do futuro — é preciso cruzar PTAX, curva B3, risco de base e compliance ESG."

**[Mostrar split-screen vazio → preencher com dashboard]**

---

## 1:00 – 2:00 | Camada orbital + Visão Computacional

**[Coluna esquerda do dashboard]**

> "Não consumimos NDVI pronto. Recebemos bandas Red e NIR e calculamos na matriz: (NIR menos Red) dividido por (NIR mais Red), com OpenCV e NumPy."

**[Apontar mapa colorido verde / amarelo / vermelho]**

> "Limiarização triclass: saudável, atenção e estresse severo. Isso alimenta o risco de safra que ajusta o basis indicativo."

---

## 2:00 – 2:45 | Edge IoT — economia de banda espacial

**[Tabela de telemetria ESP32]**

> "Na economia espacial, banda é cara. O ESP32 calcula média móvel na borda e só transmite se a umidade desviar quinze por cento da média ou na janela horária. Isso é edge computing real, não telemetria ruidosa."

**[Opcional: foto do hardware ou Wokwi]**

---

## 2:45 – 3:30 | Mercado — PTAX, B3, curva e basis

**[Coluna direita: gráficos Plotly]**

> "Capturamos PTAX via API OData do Banco Central, com scraping e CSV de fallback. Cotação soja SJC na B3 com a mesma estratégia."

**[Gráfico curva contango/backwardation]**

> "A curva de futuros reflete oferta e demanda. Abaixo, basis atual versus indicativo — a Teoria da Convergência."

---

## 3:30 – 4:15 | ESG Red Flag + Copiloto RAG

**[Ativar checkbox na sidebar: Simular Cenário de Risco ESG]**

> "Tradings não originam áreas com passivo em APP. Ativamos o Red Flag: propriedade inelegível para originação e hedge."

**[Desativar checkbox — briefing normal]**

> "O Copiloto RAG consulta ChromaDB — basis, convergência, hedge — e gera o briefing com LangChain. Modo híbrido offline; com OpenAI, modo LLM completo. Material educacional, sem promessa de rentabilidade."

---

## 4:15 – 4:45 | Arquitetura distribuída

**[Diagrama rápido ou README]**

> "FastAPI expõe `/api/v1/analysis` e `/api/v1/hardware/telemetry`. Streamlit consome o orchestrator ou a API. Módulos: NDVIProcessor, SojaBasisEngine, ESGCompliance, OrbitalOrchestrator."

---

## 4:45 – 5:00 | Encerramento

> "OrbitalBasis: da órbita ao campo, do campo ao mercado. OrbitalBasis Team. QUERO CONCORRER. Obrigado."

**[Tela final: logo FIAP + QR GitHub]**

---

## Checklist pré-gravação

- [ ] Frase **"QUERO CONCORRER"** nos primeiros 15 segundos
- [ ] Dashboard rodando (`streamlit run src/applications/dashboard/app.py`)
- [ ] API opcional rodando (`uvicorn src.applications.api.main:app`)
- [ ] Checkbox ESG testado antes da gravação
- [ ] Áudio sem ruído; resolução mínima 1080p
