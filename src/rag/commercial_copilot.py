"""
Copiloto de comercialização — briefing Markdown.

Modos (ORBITAL_RAG_MODE):
  - deterministic: template fixo (demo estável)
  - hybrid: template + trechos Chroma (padrão)
  - llm: LangChain + OpenAI quando OPENAI_API_KEY definida; senão hybrid
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from src.rag.retriever import format_retrieved_chunks, retrieve_context

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "briefing_template.txt"

HEDGE_LABELS = {
    "monitor_short_basis": "**Short Basis** (monitorar venda do físico)",
    "monitor_long_basis": "**Long Basis** (monitorar retenção do físico)",
    "hedge_basis_mismatch_risk": "**Risco de descasamento do hedge** na B3 vs prêmio regional",
    "esg_block": "**Bloqueio de originação** — sem hedge até regularização ESG",
    "neutral": "**Neutro** — monitorar convergência do basis",
}

CURVE_LABELS = {
    "contango": "Contango (muita oferta / demanda contida)",
    "backwardation": "Backwardation (oferta restrita)",
    "flat": "Curva Flat / transição",
}


def _rag_mode() -> str:
    return os.getenv("ORBITAL_RAG_MODE", "hybrid").lower()


def _build_retrieval_query(rag_context: dict) -> str:
    curve = rag_context.get("curve_shape", "flat")
    hedge = rag_context.get("hedge_stance", "neutral")
    risk = rag_context.get("yield_risk_score", 0)
    esg = rag_context.get("esg_compliant", True)
    parts = [
        "basis convergência risco de base",
        f"curva {curve}",
        f"hedge {hedge}",
        f"risco safra {risk}",
    ]
    if not esg:
        parts.append("ESG APP red flag originação bloqueada")
    return " ".join(parts)


def generate_briefing_markdown(rag_context: dict) -> str:
    """Ponto de entrada: escolhe modo RAG e gera briefing."""
    mode = _rag_mode()

    if mode == "deterministic":
        return _generate_deterministic(rag_context)

    chunks = retrieve_context(_build_retrieval_query(rag_context), k=4)
    knowledge = format_retrieved_chunks(chunks)

    if mode == "llm" or (mode == "hybrid" and os.getenv("OPENAI_API_KEY")):
        llm_text = _generate_with_langchain(rag_context, knowledge)
        if llm_text:
            return llm_text

    base = _generate_deterministic(rag_context)
    if knowledge and mode == "hybrid":
        base += "\n\n#### Referências RAG (ChromaDB)\n" + knowledge
    return base


def _generate_deterministic(rag_context: dict) -> str:
    if not rag_context.get("esg_compliant", True):
        return _esg_red_flag_briefing(rag_context)

    basis_atual = rag_context.get("basis_atual", 0)
    basis_ind = rag_context.get("basis_indicativo", 0)
    gap = rag_context.get("convergence_gap", 0)
    curve = CURVE_LABELS.get(rag_context.get("curve_shape", "flat"), "N/D")
    hedge = HEDGE_LABELS.get(rag_context.get("hedge_stance", "neutral"), "N/D")
    risk = rag_context.get("yield_risk_score", 0)
    ndvi = rag_context.get("ndvi_mean")
    soil = rag_context.get("soil_moisture_pct")
    hooks = rag_context.get("narrative_hooks") or []

    lines = [
        "### Briefing OrbitalBasis — Copiloto de Comercialização",
        "",
        "*Material educacional. Não constitui recomendação de investimento.*",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| **Basis atual** | {basis_atual:.2f} {rag_context.get('basis_unit', '')} |",
        f"| **Basis indicativo** | {basis_ind:.2f} |",
        f"| **Gap de convergência** | {gap:+.2f} |",
        f"| **Curva de futuros** | {curve} |",
        f"| **Risco de safra (orbital+IoT)** | {risk}/100 |",
    ]
    if ndvi is not None:
        lines.append(f"| **NDVI médio (campo)** | {ndvi:.3f} |")
    if soil is not None:
        lines.append(f"| **Umidade solo (ESP32)** | {soil:.1f}% |")

    lines.extend(
        [
            "",
            "#### Safra / Clima",
            f"Sinais orbitais e de borda indicam risco de safra **"
            f"{'elevado' if risk >= 60 else 'moderado' if risk >= 35 else 'contido'}**. "
            "A Teoria da Convergência sugere que o basis físico tende a fechar parte do spread "
            "em relação ao futuro padronizado.",
            "",
            "#### Risco de Base",
        ]
    )

    if risk >= 60 and gap > 1.5:
        lines.append(
            "Oferta regional pressionada: o basis local tende a **ágio**. "
            "Hedge em contrato B3 pode ficar **descasado** se o prêmio de risco regional não for modelado."
        )
    else:
        lines.append(
            "Spread físico vs tela dentro de faixa monitorável. "
            "Acompanhar convergência antes de travar hedge."
        )

    lines.extend(["", "#### Hedge educacional", hedge, ""])
    for hook in hooks:
        lines.append(f"- {hook}")

    lines.append("")
    lines.append("---")
    lines.append("*OrbitalBasis — fusão órbita → campo → mercado.*")
    return "\n".join(lines)


def _generate_with_langchain(rag_context: dict, knowledge: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except ImportError:
        logger.warning("langchain-openai não instalado — fallback hybrid")
        return None

    template = load_prompt_template()
    system_rules = (
        "Você é o Copiloto Comercial OrbitalBasis. "
        "Use APENAS os dados JSON e os trechos de conhecimento fornecidos. "
        "Material educacional — sem promessa de rentabilidade."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_rules),
            (
                "human",
                "{template}\n\n---\nCONHECIMENTO RECUPERADO (Chroma):\n{knowledge}\n\n"
                "---\nDADOS DA ANÁLISE:\n{data}",
            ),
        ]
    )

    try:
        chain = prompt | ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2) | StrOutputParser()
        return chain.invoke(
            {
                "template": template.replace("{{rag_context}}", "(ver JSON abaixo)"),
                "knowledge": knowledge or "Nenhum trecho adicional.",
                "data": json.dumps(rag_context, ensure_ascii=False, indent=2),
            }
        )
    except Exception as exc:
        logger.warning("LLM RAG falhou: %s", exc)
        return None


def _esg_red_flag_briefing(ctx: dict) -> str:
    hooks = ctx.get("narrative_hooks") or [
        "Propriedade inelegível para originação e travamento de hedge devido a inconformidade ESG."
    ]
    return "\n".join(
        [
            "### RED FLAG ESG — Originação bloqueada",
            "",
            "> **Propriedade inelegível** para originação e travamento de hedge "
            "devido a inconformidade socioambiental (APP).",
            "",
            f"- Estresse detectado em APP: **{ctx.get('esg_app_stress_pct', 'N/D')}%**",
            f"- {hooks[0]}",
            "",
            "*Regularize o passivo ambiental antes de qualquer estratégia de comercialização.*",
        ]
    )


def load_prompt_template() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return ""


def render_prompt_with_context(rag_context: dict) -> str:
    template = load_prompt_template()
    return template.replace("{{rag_context}}", json.dumps(rag_context, ensure_ascii=False, indent=2))
