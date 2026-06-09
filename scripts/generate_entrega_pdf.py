"""
Gera PDF de entrega FIAP — layout estruturado (português + figuras).
Saída: docs/OrbitalBasis_Entrega_FIAP_2026.1.pdf + cópia em Downloads
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "PDF_ENTREGA_FIAP_COPIAR_WORD.txt"
OUTPUT = ROOT / "docs" / "OrbitalBasis_Entrega_FIAP_2026.1.pdf"
DASHBOARD_ASSET = ROOT / "assets" / "dashboard_multi.png"
DOWNLOADS_COPY = Path.home() / "Downloads" / "OrbitalBasis_Entrega_FIAP_2026.1.pdf"

PAGE_W, _ = A4
CONTENT_W = PAGE_W - 4.4 * cm


def _register_fonts() -> dict[str, str]:
    win = Path("C:/Windows/Fonts")
    specs = [
        ("body", "arial.ttf", "Arial"),
        ("bold", "arialbd.ttf", "Arial-Bold"),
        ("mono", "consola.ttf", "Consolas"),
    ]
    out: dict[str, str] = {}
    for key, fname, name in specs:
        path = win / fname
        if not path.exists():
            path = win / ("calibri.ttf" if key == "body" else "calibrib.ttf")
            name = "Calibri" if key == "body" else "Calibri-Bold"
        pdfmetrics.registerFont(TTFont(name, str(path)))
        out[key] = name
    return out


def _styles(f: dict[str, str]) -> dict[str, ParagraphStyle]:
    b = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("cover", fontName=f["bold"], fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=10),
        "cover_sub": ParagraphStyle("cover_sub", fontName=f["body"], fontSize=11, leading=14, alignment=TA_CENTER, spaceAfter=6),
        "podium": ParagraphStyle("podium", fontName=f["bold"], fontSize=12, leading=15, alignment=TA_CENTER, spaceBefore=8, spaceAfter=12),
        "section": ParagraphStyle("section", fontName=f["bold"], fontSize=12, leading=15, alignment=TA_CENTER, spaceBefore=6, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName=f["bold"], fontSize=11, leading=14, spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("body", fontName=f["body"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=7),
        "bullet": ParagraphStyle("bullet", fontName=f["body"], fontSize=10, leading=13, leftIndent=14, spaceAfter=3),
        "code": ParagraphStyle("code", fontName=f["mono"], fontSize=8, leading=10, leftIndent=10, backColor=colors.HexColor("#f5f5f5"), borderPadding=6, spaceAfter=8),
        "note": ParagraphStyle("note", fontName=f["body"], fontSize=9, leading=12, textColor=colors.HexColor("#555555"), spaceAfter=6),
        "link": ParagraphStyle("link", fontName=f["body"], fontSize=10, leading=13, leftIndent=12, textColor=colors.HexColor("#1565c0"), spaceAfter=4),
        "footer": ParagraphStyle("footer", fontName=f["body"], fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceBefore=10),
    }


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    safe = re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", text)
    return Paragraph(safe, style)


def _scaled_image(path: Path) -> Image:
    img = Image(str(path))
    scale = min(CONTENT_W / img.imageWidth, 8 * cm / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    img.hAlign = "CENTER"
    return img


_SECTION_HDR = re.compile(
    r"^(?:PÁGINA \d|1\. INTRODUÇÃO|2\. DESENVOLVIMENTO|3\. RESULTADOS ESPERADOS|"
    r"4\. CONCLUSÕES|5\. LINKS DE ENTREGA)"
)


def _parse_sections(raw: str) -> dict[str, str]:
    """Divide o .txt em seções (título entre dois separadores ═══ + corpo seguinte)."""
    text = raw.split("FIM DO DOCUMENTO")[0]
    start = text.find("PÁGINA 1")
    if start >= 0:
        text = text[start:]
    chunks = [c.strip() for c in re.split(r"\n═{20,}\n", text) if c.strip()]
    sections: dict[str, str] = {}
    i = 0
    while i < len(chunks):
        lines = chunks[i].splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if _SECTION_HDR.match(title) and not body:
            i += 1
            if i < len(chunks):
                sections[title] = chunks[i]
                i += 1
            continue
        if _SECTION_HDR.match(title) and body:
            sections[title] = body
        i += 1
    return sections


def _body_paragraphs(text: str, s: dict) -> list:
    """Converte texto livre em parágrafos (sem engolir subseções)."""
    story: list = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if re.match(r"^\d+\.\d+\s+", line):
            story.append(_p(line, s["h2"]))
            i += 1
            continue
        if line.endswith(":") and len(line) < 80 and not line.startswith("http"):
            story.append(_p(f"<b>{line}</b>", s["body"]))
            i += 1
            continue
        if line.startswith("http"):
            story.append(_p(line, s["link"]))
            i += 1
            continue
        if line.startswith("(") and "Ajuste" in line:
            story.append(_p(f"<i>{line}</i>", s["note"]))
            i += 1
            continue
        if line.startswith("Frase de encerramento:"):
            story.append(_p(f"<b>{line}</b>", s["body"]))
            i += 1
            continue
        if line.startswith("    "):
            block = []
            while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                if lines[i].strip():
                    block.append(lines[i][4:])
                elif block:
                    break
                i += 1
            joined = "\n".join(block)
            if any(k in joined for k in ("def ", "if ", "return ", "python ", "pytest", "uvicorn", "streamlit", "cd ", "pip ")):
                story.append(Preformatted(joined, s["code"]))
            else:
                for b in block:
                    story.append(_p(b, s["bullet"]))
            continue
        if line == "OrbitalBasis Team. QUERO CONCORRER.":
            story.append(_p(line, s["podium"]))
            i += 1
            continue
        if line.startswith("[ESPAÇO RESERVADO"):
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or re.match(r"^\d+\.\d+\s+", nxt) or nxt.startswith("    ") or nxt.startswith("http") or nxt.endswith(":") and len(nxt) < 80 or nxt.startswith("[ESPAÇO") or nxt == "OrbitalBasis Team. QUERO CONCORRER.":
                break
            para.append(nxt)
            i += 1
        story.append(_p(" ".join(para), s["body"]))
    return story


def _cover_page(s: dict) -> list:
    integrantes = [
        ["Tiago Alves Cordeiro", "561791", "561791@fiap.com.br"],
        ["Leandro Arthur Marinho Ferreira", "565240", "565240@fiap.com.br"],
        ["Otavio Custodio de Oliveira", "565606", "565606@fiap.com.br"],
        ["Matheus José Parra", "561907", "561907@fiap.com.br"],
    ]
    table = Table(
        [["Nome", "RM", "E-mail"]] + integrantes,
        colWidths=[7.2 * cm, 2.2 * cm, 5.6 * cm],
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), s["h2"].fontName),
                ("FONTNAME", (0, 1), (-1, -1), s["body"].fontName),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef3")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Spacer(1, 0.5 * cm),
        _p("PÁGINA 1 — IDENTIFICAÇÃO", s["cover"]),
        _p("Global Solution FIAP 2026.1 · A Nova Economia Espacial", s["cover_sub"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a1a2e")),
        Spacer(1, 0.4 * cm),
        _p("OrbitalBasis Team. QUERO CONCORRER.", s["podium"]),
        Spacer(1, 0.2 * cm),
        _p("<b>Integrantes</b>", s["body"]),
        table,
        Spacer(1, 0.25 * cm),
        _p("<i>(Ajuste os e-mails se o formato institucional da turma for diferente.)</i>", s["note"]),
        Spacer(1, 0.3 * cm),
        _p("<b>Título do projeto:</b> OrbitalBasis — Copiloto Orbital de Comercialização Agrícola", s["body"]),
        _p("<b>Disciplina / entrega:</b> Global Solution FIAP 2026.1 — A Nova Economia Espacial", s["body"]),
        _p("<b>Curso:</b> Inteligência Artificial — 2º ano · Prova de Conceito (POC) e MVP funcional", s["body"]),
        PageBreak(),
    ]


def _section_block(title: str, body: str, s: dict, *, with_figure: bool = False) -> list:
    story = [
        _p(title, s["section"]),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#999999")),
        Spacer(1, 0.15 * cm),
    ]
    story.extend(_body_paragraphs(body, s))
    if with_figure and DASHBOARD_ASSET.exists():
        story.append(Spacer(1, 0.35 * cm))
        fig = KeepTogether(
            [
                _scaled_image(DASHBOARD_ASSET),
                Spacer(1, 0.15 * cm),
                _p(
                    "<i>Figura 1 — Dashboard OrbitalBasis (cenário ESG OK, ML ativo).</i>",
                    s["note"],
                ),
            ]
        )
        story.append(fig)
    story.append(PageBreak())
    return story


def build_story() -> list:
    fonts = _register_fonts()
    s = _styles(fonts)
    sections = _parse_sections(SOURCE.read_text(encoding="utf-8"))

    story: list = []
    story.extend(_cover_page(s))

    mapping = [
        ("1. INTRODUÇÃO", "1. INTRODUÇÃO"),
        ("2. DESENVOLVIMENTO", "2. DESENVOLVIMENTO"),
        ("3. RESULTADOS ESPERADOS", "3. RESULTADOS ESPERADOS"),
        ("4. CONCLUSÕES", "4. CONCLUSÕES"),
        ("5. LINKS DE ENTREGA (ÚLTIMA PÁGINA — OBRIGATÓRIO)", "5. LINKS DE ENTREGA"),
    ]

    for key_fragment, display_title in mapping:
        body = ""
        for title, content in sections.items():
            if key_fragment in title:
                body = content
                break
        if not body:
            continue
        with_fig = "RESULTADOS" in key_fragment
        story.extend(_section_block(display_title, body, s, with_figure=with_fig))

    story.append(
        _p("FIM DO DOCUMENTO — OrbitalBasis Team · Global Solution FIAP 2026.1", s["footer"])
    )
    return story


def main() -> Path:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

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
    doc.build(build_story())
    print(f"PDF gerado: {OUTPUT}")
    print(f"Tamanho: {OUTPUT.stat().st_size / 1024:.1f} KB")

    try:
        shutil.copy2(OUTPUT, DOWNLOADS_COPY)
        print(f"Copia salva em Downloads: {DOWNLOADS_COPY}")
    except PermissionError:
        alt = DOWNLOADS_COPY.with_name(DOWNLOADS_COPY.stem + "_NOVO.pdf")
        shutil.copy2(OUTPUT, alt)
        print(f"Downloads bloqueado (feche o PDF aberto). Copia alternativa: {alt}")
    return OUTPUT


if __name__ == "__main__":
    main()
