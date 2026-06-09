"""
Gera PDF de entrega FIAP espelhando docs/PDF_ENTREGA_FIAP_COPIAR_WORD.txt
Saída: docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "PDF_ENTREGA_FIAP_COPIAR_WORD.txt"
OUTPUT = ROOT / "docs" / "OrbitalBasis_Entrega_FIAP_2026.1.pdf"
DASHBOARD_ASSET = ROOT / "assets" / "dashboard_demo.png"

SEP_HEAVY = re.compile(r"^═+$")
SEP_LIGHT = re.compile(r"^=+$")
INDENT = re.compile(r"^    \S")


def _styles():
    base = getSampleStyleSheet()
    return {
        "section": ParagraphStyle(
            "section",
            parent=base["Heading1"],
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "podium": ParagraphStyle(
            "podium",
            parent=base["Normal"],
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=10,
            fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=10,
            leading=13,
            spaceBefore=10,
            spaceAfter=5,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "indent": ParagraphStyle(
            "indent",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            leftIndent=20,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            leftIndent=16,
            rightIndent=8,
            backColor=colors.HexColor("#f5f5f5"),
            borderColor=colors.HexColor("#dddddd"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=8,
        ),
        "note": ParagraphStyle(
            "note",
            parent=base["Italic"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#444444"),
            spaceAfter=7,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#666666"),
            spaceBefore=12,
        ),
    }


def _load_body_lines() -> list[str]:
    raw = SOURCE.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    started = False
    for line in raw:
        if "FIM DO DOCUMENTO" in line:
            break
        if not started:
            if "PÁGINA 1" in line:
                started = True
            continue
        out.append(line.rstrip())
    while out and not out[-1].strip():
        out.pop()
    return out


def _is_subsection(line: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\s+\S", line.strip()))


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_story_from_txt() -> list:
    s = _styles()
    story: list = []
    lines = _load_body_lines()
    i = 0
    page_break_sections = {
        "3. RESULTADOS ESPERADOS",
        "4. CONCLUSÕES",
        "5. LINKS DE ENTREGA",
    }

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if SEP_HEAVY.match(stripped):
            # collect title until next heavy sep or content
            i += 1
            title_parts: list[str] = []
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt:
                    i += 1
                    continue
                if SEP_HEAVY.match(nxt):
                    i += 1
                    break
                title_parts.append(nxt)
                i += 1
            title = " ".join(title_parts).strip()
            if title:
                if any(title.startswith(sec) for sec in page_break_sections):
                    story.append(PageBreak())
                story.append(Spacer(1, 0.2 * cm))
                story.append(Paragraph(_escape_xml(title), s["section"]))
                story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#999999")))
            continue

        if stripped == "OrbitalBasis Team. QUERO CONCORRER.":
            story.append(Paragraph(_escape_xml(stripped), s["podium"]))
            i += 1
            continue

        if stripped.startswith("[ESPAÇO RESERVADO"):
            if DASHBOARD_ASSET.exists():
                img = Image(str(DASHBOARD_ASSET), width=14 * cm, height=7.9 * cm)
                story.append(Spacer(1, 0.2 * cm))
                story.append(img)
                story.append(
                    Paragraph(
                        "<i>Figura 1 — Dashboard OrbitalBasis (demo ESG OK). "
                        "Fonte: assets/dashboard_demo.png</i>",
                        s["note"],
                    )
                )
            else:
                story.append(Paragraph(f"<i>{_escape_xml(stripped)}</i>", s["note"]))
            i += 1
            continue

        if stripped.startswith("(") and stripped.endswith(")") and "Ajuste" in stripped:
            story.append(Paragraph(f"<i>{_escape_xml(stripped)}</i>", s["note"]))
            i += 1
            continue

        if _is_subsection(stripped):
            story.append(Paragraph(_escape_xml(stripped), s["h2"]))
            i += 1
            continue

        if stripped.endswith(":") and not INDENT.match(line):
            story.append(Paragraph(f"<b>{_escape_xml(stripped)}</b>", s["body"]))
            i += 1
            continue

        # Indented block (code or lista)
        if INDENT.match(line):
            block: list[str] = []
            while i < len(lines) and (INDENT.match(lines[i]) or (lines[i].strip() == "" and i + 1 < len(lines) and INDENT.match(lines[i + 1]))):
                if lines[i].strip():
                    block.append(lines[i][4:])
                elif block:
                    break
                i += 1
            text = "\n".join(block)
            if any(k in text for k in ("def ", "if ", "return ", "python ", "pytest", "uvicorn", "streamlit", "cd ", "pip ")):
                story.append(Preformatted(text, s["code"]))
            else:
                for bl in block:
                    story.append(Paragraph(_escape_xml(bl), s["indent"]))
            continue

        if stripped.startswith("Frase de encerramento:"):
            story.append(Paragraph(f"<b>{_escape_xml(stripped)}</b>", s["body"]))
            i += 1
            continue

        # Parágrafo normal — agrupa linhas contínuas
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or SEP_HEAVY.match(nxt)
                or INDENT.match(lines[i])
                or _is_subsection(nxt)
                or nxt == "OrbitalBasis Team. QUERO CONCORRER."
                or nxt.endswith(":") and len(nxt) < 80
                or nxt.startswith("[ESPAÇO")
            ):
                break
            para.append(nxt)
            i += 1
        story.append(Paragraph(_escape_xml(" ".join(para)), s["body"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="60%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(
        Paragraph(
            "FIM DO DOCUMENTO — OrbitalBasis Team · Global Solution FIAP 2026.1",
            s["footer"],
        )
    )
    return story


def main() -> Path:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Fonte não encontrada: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="OrbitalBasis — Entrega FIAP 2026.1",
        author="OrbitalBasis Team",
    )
    doc.build(build_story_from_txt())
    print(f"PDF gerado (formato .txt): {OUTPUT}")
    print(f"Tamanho: {OUTPUT.stat().st_size / 1024:.1f} KB")
    return OUTPUT


if __name__ == "__main__":
    main()
