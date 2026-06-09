# OrbitalBasis - Análise do Projeto

## 1. Visão Geral
O **OrbitalBasis** é um copiloto de comercialização agrícola baseado na Economia Espacial. O sistema une dados espaciais (NDVI via satélite), IoT na borda (sensores ESP32) e dados do mercado físico de commodities para prever o risco da safra e aplicar governança ESG.

## 2. Arquitetura Atual
Atualmente, o projeto é dividido em dois serviços principais e vários módulos de domínio:
- **Front-end**: Streamlit (Dashboard interativo em `src/applications/dashboard/app.py`).
- **Back-end**: FastAPI (`src/applications/api/main.py`), servindo rotas REST na porta 8000.

### 2.1. Endpoints da API (FastAPI)
- `GET/POST /api/v1/analysis`: Roda a lógica central (Orchestrator). Ingesta dados manuais ou de telemetria, aciona o modelo de Machine Learning para risco de safra, calcula o *basis* da commodity e verifica restrições ESG.
- `POST /api/v1/hardware/telemetry`: Endpoint para recebimento de dados (JSON) dos sensores IoT (ESP32).
- `GET /api/v1/hardware/telemetry`: Retorna as leituras recentes dos sensores.
- `GET /health`: Healthcheck.

### 2.2. Módulos de Domínio (`src/`)
- **`core_logic`**: Regras de negócio puras (cálculo financeiro de Basis, validação ESG).
- **`data_collection`**: Ingestão de dados de telemetria e simuladores.
- **`market_data`**: Integração com PTAX/B3 e Web Scraping.
- **`ml_models`**: Carrega e processa o modelo Random Forest (`yield_risk_v1.joblib`) via `scikit-learn` e processa matrizes de imagem com `OpenCV`.
- **`rag`**: RAG usando LangChain e banco vetorial local (ChromaDB) para geração de resumos baseados em contexto restrito.

## 3. Avaliação de Maturidade e Limitações
- **Vantagens**: A base em Python é extremamente robusta para IA (scikit-learn, LangChain) e Visão Computacional (OpenCV). A API em FastAPI é assíncrona e rápida.
- **Limitações**: O uso do Streamlit no Front-end é ótimo para provas de conceito (PoC) e MVP, mas não escala bem para um produto SaaS final que exija micro-interações, design fluido, customização extrema de CSS e alta performance no lado do cliente.

## 4. Oportunidades de Aperfeiçoamento (React)
Para transformar o MVP em um produto "premium" e de classe mundial, a arquitetura deve evoluir para separar estritamente a interface do motor de IA:
1. **Front-end Moderno**: Migração do Streamlit para **React** (ex: Vite ou Next.js).
2. **Back-end em Camadas**: O novo back-end React (Node.js/Next.js) atuará como um BFF (Backend-For-Frontend) ou gerenciará a autenticação e sessões, enquanto a API FastAPI atual será mantida como um microsserviço especialista ("AI Engine").
