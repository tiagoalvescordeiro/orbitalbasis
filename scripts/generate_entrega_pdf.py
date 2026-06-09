"""
Gera PDF único de entrega FIAP a partir do conteúdo documentado.
Saída: docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "OrbitalBasis_Entrega_FIAP_2026.1.pdf"


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Heading1"],
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "podium": ParagraphStyle(
            "podium",
            parent=base["Normal"],
            fontSize=13,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=14,
            fontName="Helvetica-Bold",
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontSize=13,
            leading=16,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#16213e"),
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            leftIndent=18,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base["Code"],
            fontSize=8,
            leading=10,
            leftIndent=12,
            backColor=colors.HexColor("#f4f4f4"),
            spaceAfter=8,
        ),
        "link": ParagraphStyle(
            "link",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#0d47a1"),
            spaceAfter=6,
        ),
        "note": ParagraphStyle(
            "note",
            parent=base["Italic"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#555555"),
            spaceAfter=8,
        ),
    }


def build_story():
    s = _styles()
    story = []

    # --- Página 1 ---
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Global Solution FIAP 2026.1", s["title"]))
    story.append(Paragraph("A Nova Economia Espacial", s["title"]))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("OrbitalBasis Team. QUERO CONCORRER.", s["podium"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Integrantes</b>", s["h2"]))
    for line in [
        "Tiago Alves Cordeiro — RM 561791 — 561791@fiap.com.br",
        "Leandro Arthur Marinho Ferreira — RM 565240 — 565240@fiap.com.br",
        "Otavio Custodio de Oliveira — RM 565606 — 565606@fiap.com.br",
        "Matheus José Parra — RM 561907 — 561907@fiap.com.br",
    ]:
        story.append(Paragraph(line, s["bullet"]))
    story.append(Paragraph(
        "<i>Ajuste os e-mails se o formato institucional da turma for diferente.</i>",
        s["note"],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "<b>Título:</b> OrbitalBasis — Copiloto Orbital de Comercialização Agrícola",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>Entrega:</b> Prova de Conceito (POC) e MVP funcional — "
        "Inteligência Artificial, 2º ano",
        s["body"],
    ))
    story.append(PageBreak())

    # --- 1. Introdução ---
    story.append(Paragraph("1. INTRODUÇÃO", s["h1"]))
    story.append(Paragraph(
        "O agronegócio brasileiro opera com informações fragmentadas: o produtor enxerga "
        "clima e solo; a mesa de operações enxerga basis, curva de futuros e câmbio. Poucas "
        "ferramentas unem dados orbitais (satélite), telemetria de borda (IoT) e indicadores "
        "financeiros em um fluxo único de decisão com governança ESG.",
        s["body"],
    ))
    story.append(Paragraph(
        "O <b>OrbitalBasis</b> é uma POC/MVP que demonstra essa integração: processamento de "
        "NDVI por visão computacional, predição de risco de safra por Machine Learning, motor "
        "de basis e PPE (PTAX BCB e B3), compliance ESG automatizado (Red Flag em APP) e "
        "copiloto comercial com RAG (ChromaDB e LangChain).",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>Escopo:</b> bandas sintéticas e datasets de fallback; métricas de ML sobre rótulos "
        "heurísticos (transparência acadêmica). Material educacional — não constitui "
        "recomendação de investimento.",
        s["body"],
    ))

    # --- 2. Desenvolvimento ---
    story.append(Paragraph("2. DESENVOLVIMENTO", s["h1"]))
    story.append(Paragraph("2.1 Arquitetura geral", s["h2"]))
    for line in [
        "(1) Órbita — NDVI matricial e segmentação (OpenCV/NumPy).",
        "(2) Campo — ESP32 com filtragem na borda.",
        "(3) Mercado — PTAX, B3, curva de futuros, basis, briefing RAG.",
        "Distribuído: FastAPI (/api/v1/analysis) + Streamlit.",
    ]:
        story.append(Paragraph(line, s["bullet"]))

    story.append(Paragraph("2.2 Visão computacional — NDVI", s["h2"]))
    story.append(Preformatted(
        "def compute_ndvi_matrix(red, nir):\n"
        "    # NDVI = (NIR - Red) / (NIR + Red)\n"
        "    red_f = red.astype('float32')\n"
        "    nir_f = nir.astype('float32')\n"
        "    denom = nir_f + red_f\n"
        "    denom = where(denom == 0, nan, denom)\n"
        "    return (nir_f - red_f) / denom",
        s["code"],
    ))

    story.append(Paragraph("2.3 Machine Learning — risco de safra", s["h2"]))
    story.append(Paragraph(
        "RandomForestRegressor (120 estimadores). Alvo: yield_risk_score (0–100). "
        "Features: ndvi_mean, ndvi_std, stress_pct_*, soil_moisture_pct.",
        s["body"],
    ))
    story.append(Preformatted(
        "python scripts/generate_training_dataset.py --rows 8000\n"
        "python scripts/train_yield_risk.py",
        s["code"],
    ))
    story.append(Paragraph(
        "Métricas: MAE = 0,024 | R² = 0,9999 | 8.000 amostras (treino 6.400 / teste 1.600).",
        s["body"],
    ))
    story.append(Preformatted(
        "def ml_enabled():\n"
        "    if getenv('ORBITAL_USE_ML_YIELD_RISK', 'true') == 'false':\n"
        "        return False\n"
        "    return Path('models/yield_risk_v1.joblib').exists()",
        s["code"],
    ))
    story.append(Paragraph(
        "<i>Nota: R² elevado reflete dataset sintético; produção exigiria rótulos de safra reais.</i>",
        s["note"],
    ))

    story.append(Paragraph("2.4 Motor de mercado", s["h2"]))
    story.append(Paragraph(
        "SojaBasisEngine: basis atual, indicativo ajustado por risco de safra, convergência, "
        "contango/backwardation.",
        s["body"],
    ))

    story.append(Paragraph("2.5 Governança ESG", s["h2"]))
    story.append(Preformatted(
        "if not yield_ctx.esg_compliant:\n"
        "    return BasisResult(\n"
        "        commodity='soja',\n"
        "        basis_atual=0.0,\n"
        "        basis_indicativo=0.0,\n"
        "        hedge_stance=ESG_BLOCK,\n"
        "    )",
        s["code"],
    ))

    story.append(Paragraph("2.6 IoT, RAG e testes", s["h2"]))
    for line in [
        "ESP32: transmissão se desvio ≥ 15% ou janela horária.",
        "RAG: ChromaDB + LangChain (deterministic / hybrid / llm).",
        "pytest: 25 testes automatizados.",
    ]:
        story.append(Paragraph(line, s["bullet"]))

    story.append(Paragraph("2.7 Integração Fases 3 e 4 (FIAP)", s["h2"]))
    for line in [
        "Visão computacional — NDVI OpenCV",
        "Machine Learning — Random Forest + yield_risk_predictor.py",
        "IA generativa — RAG ChromaDB + LangChain",
        "IoT / Edge — firmware ESP32",
        "Apps distribuídas — FastAPI + Streamlit",
        "Web scraping — PTAX BCB + B3",
    ]:
        story.append(Paragraph(line, s["bullet"]))

    story.append(Paragraph("2.8 Como executar", s["h2"]))
    story.append(Preformatted(
        "pip install -r requirements.txt\n"
        "pytest tests/ -q\n"
        "uvicorn src.applications.api.main:app --reload --port 8000\n"
        "streamlit run src/applications/dashboard/app.py",
        s["code"],
    ))
    story.append(PageBreak())

    # --- 3. Resultados ---
    story.append(Paragraph("3. RESULTADOS ESPERADOS", s["h1"]))
    for line in [
        "Dashboard com Campo (NDVI, risco safra) e Mercado (curva, basis).",
        "ML ativo na sidebar (ex.: risco 64/100).",
        "ESG OK padrão; RED FLAG simulado bloqueia basis.",
        "API JSON: ndvi_summary, esg, basis, briefing_markdown.",
        "Métricas ML reproduzíveis (MAE 0,024; R² 0,9999).",
    ]:
        story.append(Paragraph(f"• {line}", s["bullet"]))
    story.append(Paragraph(
        "<i>Evidência visual: vídeo demonstrativo e dashboard em "
        "http://127.0.0.1:8501 (ver repositório).</i>",
        s["note"],
    ))

    # --- 4. Conclusões ---
    story.append(Paragraph("4. CONCLUSÕES", s["h1"]))
    story.append(Paragraph(
        "O OrbitalBasis cumpre o escopo da Global Solution 2026.1: órbita, campo e mercado "
        "integrados com ML, ESG e camada distribuída demonstrável em vídeo de até 5 minutos.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>Limitações:</b> dados sintéticos, labels heurísticos, APP em máscara demo.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>OrbitalBasis:</b> da órbita ao campo, do campo ao mercado. "
        "<b>OrbitalBasis Team. QUERO CONCORRER.</b>",
        s["podium"],
    ))
    story.append(PageBreak())

    # --- 5. Links ---
    story.append(Paragraph("5. LINKS DE ENTREGA", s["h1"]))
    story.append(Paragraph(
        "<b>Repositório GitHub:</b><br/>"
        "https://github.com/tiagoalvescordeiro/orbitalbasis",
        s["link"],
    ))
    story.append(Paragraph(
        "<b>Vídeo (YouTube — NÃO LISTADO):</b><br/>"
        "[Inserir URL após gravação]",
        s["link"],
    ))
    story.append(Paragraph(
        "<b>Arquitetura:</b><br/>"
        "https://github.com/tiagoalvescordeiro/orbitalbasis/blob/main/docs/ARQUITETURA.md",
        s["link"],
    ))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Material educacional. Não constitui recomendação de investimento.",
        s["note"],
    ))

    return story


def main() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="OrbitalBasis — Entrega FIAP 2026.1",
        author="OrbitalBasis Team",
    )
    doc.build(build_story())
    print(f"PDF gerado: {OUTPUT}")
    print(f"Tamanho: {OUTPUT.stat().st_size / 1024:.1f} KB")
    return OUTPUT


if __name__ == "__main__":
    main()
