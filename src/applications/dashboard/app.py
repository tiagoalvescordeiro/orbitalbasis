"""
OrbitalBasis — Dashboard Streamlit (Global Solution 2026.1).

Execução:
  streamlit run src/applications/dashboard/app.py
"""

from __future__ import annotations

import base64
import logging
import os
import sys
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import plotly.graph_objects as go
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core_logic.orchestrator import OrbitalOrchestrator, analysis_to_dict
from src.data_collection.serial_mqtt_reader import get_telemetry_store
from src.rag.commercial_copilot import generate_briefing_markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbitalbasis.dashboard")

API_URL = os.getenv("ORBITAL_API_URL", "http://127.0.0.1:8000")
USE_API = os.getenv("ORBITAL_USE_API", "false").lower() == "true"

st.set_page_config(
    page_title="OrbitalBasis | FIAP Global Solution",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS cinematográfico ---
st.markdown(
    """
    <style>
    .main-header { font-size: 2rem; font-weight: 700; color: #0e3d5c; }
    .esg-ok { padding: 1rem; border-radius: 8px; background: #e8f5e9; border-left: 6px solid #2e7d32; }
    .esg-red { padding: 1rem; border-radius: 8px; background: #ffebee; border-left: 6px solid #c62828; }
    .metric-card { background: #f5f9fc; padding: 0.75rem; border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_orchestrator() -> OrbitalOrchestrator:
    return OrbitalOrchestrator()


@st.cache_resource
def get_telemetry():
    store = get_telemetry_store()
    store.start_simulator(interval_sec=6.0)
    return store


def fetch_analysis(esg_red_flag: bool, soil: float, saca: float) -> dict:
    if USE_API:
        try:
            resp = requests.get(
                f"{API_URL}/api/v1/analysis",
                params={
                    "esg_red_flag": esg_red_flag,
                    "soil_moisture_pct": soil,
                    "saca_rs": saca,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("API indisponível, modo local: %s", exc)
            st.sidebar.warning("API offline — usando orchestrator local.")

    orch = get_orchestrator()
    moisture = get_telemetry().latest_moisture() or soil
    analysis = orch.run(
        soil_moisture_pct=moisture,
        esg_red_flag_demo=esg_red_flag,
        saca_rs=saca,
    )
    return analysis_to_dict(analysis)


def b64_to_image(b64_str: str) -> np.ndarray:
    raw = base64.b64decode(b64_str)
    arr = np.frombuffer(raw, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def plot_futures_curve(prices: list[float], curve_shape: str) -> go.Figure:
    labels = ["M1 (curto)", "M2", "M3 (longo)"]
    colors = {"contango": "#1565c0", "backwardation": "#e65100", "flat": "#546e7a"}
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels[: len(prices)],
            y=prices,
            mode="lines+markers",
            name="Curva de Futuros",
            line=dict(color=colors.get(curve_shape, "#1565c0"), width=3),
            marker=dict(size=12),
        )
    )
    fig.update_layout(
        title=f"Curva de Futuros — {curve_shape.upper()}",
        yaxis_title="Cents USD / bu (referência)",
        template="plotly_white",
        height=320,
    )
    return fig


def plot_basis(basis_atual: float, basis_ind: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Basis Atual", "Basis Indicativo"],
            y=[basis_atual, basis_ind],
            marker_color=["#1976d2", "#43a047"],
            text=[f"{basis_atual:.2f}", f"{basis_ind:.2f}"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Basis Atual vs Indicativo (Convergência)",
        yaxis_title="Pontos / R$ conforme unidade",
        template="plotly_white",
        height=320,
    )
    return fig


def main() -> None:
    telemetry = get_telemetry()

    st.markdown('<p class="main-header">🛰️ OrbitalBasis — Copiloto Orbital de Comercialização</p>', unsafe_allow_html=True)
    st.caption("Global Solution 2026.1 · Economia Espacial · Soja Oeste SC · FIAP IA 2º ano")

    with st.sidebar:
        st.header("Controles de Demo")
        esg_red = st.checkbox(
            "Simular Cenário de Risco ESG (Red Flag)",
            value=False,
            help="Ativa violação simulada em APP — bloqueio de originação.",
        )
        saca = st.number_input("Preço físico (R$/saca)", value=138.50, step=0.5)
        soil_manual = st.slider("Umidade solo manual (%)", 10.0, 50.0, 22.0, 0.5)
        refresh = st.button("Atualizar análise", type="primary")
        st.divider()
        st.markdown("**Legenda NDVI**")
        st.markdown("🟢 Saudável · 🟡 Atenção · 🔴 Estresse severo")
        st.markdown("**Fontes de mercado**")
        st.caption("PTAX: BCB OData + fallback CSV")
        st.caption("B3 SJC: scraping + fallback CSV")
        rag_mode = os.getenv("ORBITAL_RAG_MODE", "hybrid")
        st.markdown("**Copiloto RAG**")
        st.caption(f"Modo: `{rag_mode}` · ChromaDB + LangChain")
        if os.getenv("OPENAI_API_KEY"):
            st.success("OPENAI_API_KEY detectada (modo LLM disponível)")
        else:
            st.info("Sem API OpenAI — hybrid determinístico + Chroma")

    if refresh or "payload" not in st.session_state:
        with st.spinner("Processando órbita → campo → mercado..."):
            try:
                st.session_state["payload"] = fetch_analysis(esg_red, soil_manual, saca)
            except Exception as exc:
                st.error(f"Erro na análise: {exc}")
                logger.exception("Dashboard analysis failed")
                return

    data = st.session_state["payload"]
    basis = data["basis"]
    esg = data["esg"]
    ndvi = data["ndvi_summary"]
    market_meta = data.get("market_meta", {})

    with st.sidebar:
        st.divider()
        st.markdown("### Fontes de Dados")
        ptax = market_meta.get("ptax_fonte", "")
        if "bcb_odata" in ptax:
            st.sidebar.success("PTAX: API oficial BCB")
        elif "scrape" in ptax:
            st.sidebar.warning("PTAX: Web scraping (fallback)")
        else:
            st.sidebar.error("PTAX: Dataset sintético")

        b3 = market_meta.get("b3_fonte", "")
        if "b3_scrape" in b3 or "scrape" in b3:
            st.sidebar.warning("B3: Web scraping")
        elif "csv" in b3:
            st.sidebar.error("B3: Dataset sintético")
        else:
            st.sidebar.info(f"B3: {b3 or 'sintético'}")

    # --- ESG Banner ---
    if esg["red_flag"]:
        st.markdown(
            f'<div class="esg-red"><strong>RED FLAG ESG</strong><br>{esg["message"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="esg-ok"><strong>ESG OK</strong> — {esg["message"]}</div>',
            unsafe_allow_html=True,
        )

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Campo — Órbita + Edge IoT")
        img_col1, img_col2 = st.columns(2)
        overlay = b64_to_image(data["ndvi_overlay_png_b64"])
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

        with img_col1:
            st.markdown("**Talhão — referência**")
            base = np.full_like(overlay_rgb, 220)
            st.image(base, caption="Área demo Oeste SC", use_container_width=True)

        with img_col2:
            st.markdown("**NDVI processado (OpenCV)**")
            st.image(overlay_rgb, caption="Segmentação: verde / amarelo / vermelho", use_container_width=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("NDVI médio", f"{ndvi.get('ndvi_mean', 0):.3f}")
        m2.metric("Estresse severo", f"{ndvi.get('stress_pct_severe', 0):.1f}%")
        m3.metric("Risco safra", f"{ndvi.get('yield_risk_hint', 0)}/100")
        m4.metric("APP stress", f"{esg.get('app_stress_pct', 0):.1f}%")

        st.markdown("**Telemetria ESP32 (edge-filtered)**")
        logs = telemetry.get_recent(12)
        if logs:
            st.dataframe(logs, use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando pacotes do ESP32 (anomalia ≥15% ou janela horária).")

    with col_right:
        st.subheader("Mercado — Basis & Curva B3")
        if market_meta:
            st.caption(
                f"PTAX: {market_meta.get('ptax_fonte', '—')} · "
                f"B3: {market_meta.get('b3_fonte', '—')} · "
                f"Contrato: {market_meta.get('b3_contract', 'SJC')}"
            )

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(
                plot_futures_curve(
                    data["futures_curve"]["prices"],
                    basis["curve_shape"],
                ),
                use_container_width=True,
            )
        with chart_col2:
            st.plotly_chart(
                plot_basis(basis["basis_atual"], basis["basis_indicativo"]),
                use_container_width=True,
            )

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        b1.metric("Basis atual", f"{basis['basis_atual']:.2f}")
        b2.metric("Basis indicativo", f"{basis['basis_indicativo']:.2f}")
        b3.metric("Gap convergência", f"{basis['convergence_gap']:+.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

        if basis.get("ppe_hint_rs_saca"):
            st.metric("PPE hint (R$/saca)", f"{basis['ppe_hint_rs_saca']:.2f}")

    st.divider()
    st.subheader("Copiloto de Comercialização RAG")
    st.markdown(data.get("briefing_markdown") or generate_briefing_markdown(data.get("rag_context", {})))

    st.caption(
        "Material educacional. Não constitui recomendação de investimento. "
        "OrbitalBasis — fusão dados órbita-campo-mercado."
    )


if __name__ == "__main__":
    main()
