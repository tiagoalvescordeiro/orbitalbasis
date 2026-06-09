"""
Gera assets visuais para entrega FIAP (dashboard, NDVI, arquitetura, IoT).

Uso:
  python scripts/generate_assets.py
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import cv2
import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ASSETS = ROOT / "assets"
ESP32_DIR = ASSETS / "esp32"
LOGO_URL = (
    "https://raw.githubusercontent.com/CaiqueFiap-2026/TEMPLATE-TIAO-2026/"
    "main/assets/logo-fiap.png"
)


def _ensure_dirs() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    ESP32_DIR.mkdir(parents=True, exist_ok=True)


def _decode_overlay_b64(b64_str: str) -> np.ndarray:
    raw = base64.b64decode(b64_str)
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Falha ao decodificar overlay NDVI")
    return img


def _put_lines(
    canvas: np.ndarray,
    lines: list[str],
    origin: tuple[int, int],
    color: tuple[int, int, int] = (30, 30, 30),
    scale: float = 0.62,
) -> None:
    x, y = origin
    for line in lines:
        cv2.putText(
            canvas,
            line,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            1,
            cv2.LINE_AA,
        )
        y += int(34 * scale / 0.62)


def save_ndvi_sample() -> Path:
    from src.ml_models.ndvi_processor import process_demo_synthetic

    result = process_demo_synthetic(seed=42, stress_fraction=0.28)
    out = ASSETS / "ndvi_overlay_sample.png"
    cv2.imwrite(str(out), result.overlay_bgr)
    return out


def save_dashboard_composite(esg_red_flag: bool, filename: str, title: str) -> Path:
    from src.core_logic.orchestrator import OrbitalOrchestrator, analysis_to_dict

    payload = analysis_to_dict(OrbitalOrchestrator().run(esg_red_flag_demo=esg_red_flag))
    w, h = 1280, 720
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 245

    header_color = (14, 61, 92) if not esg_red_flag else (92, 14, 14)
    cv2.rectangle(canvas, (0, 0), (w, 58), header_color, -1)
    cv2.putText(
        canvas,
        title,
        (24, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.95,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    overlay = _decode_overlay_b64(payload["ndvi_overlay_png_b64"])
    overlay = cv2.resize(overlay, (420, 420))
    canvas[78:498, 32:452] = overlay
    cv2.putText(
        canvas,
        "NDVI (OpenCV)",
        (32, 520),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (60, 60, 60),
        1,
        cv2.LINE_AA,
    )

    esg = payload["esg"]
    basis = payload["basis"]
    ndvi = payload["ndvi_summary"]
    risk = payload.get("rag_context", {}).get("yield_risk_score", ndvi.get("yield_risk_hint", 0))

    if esg["red_flag"]:
        cv2.rectangle(canvas, (470, 72), (w - 24, 210), (0, 0, 210), 2)
        cv2.putText(
            canvas,
            "RED FLAG ESG",
            (490, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 200),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Origem bloqueada",
            (490, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 160),
            1,
            cv2.LINE_AA,
        )

    lines = [
        f"NDVI medio: {ndvi.get('ndvi_mean', 0):.3f}",
        f"Estresse severo: {ndvi.get('stress_pct_severe', 0):.1f}%",
        f"Risco safra: {risk}/100",
        f"Basis atual: {basis['basis_atual']:.2f}",
        f"Basis indicativo: {basis['basis_indicativo']:.2f}",
        f"Gap convergencia: {basis['convergence_gap']:+.2f}",
        f"Curva: {basis['curve_shape']}",
        f"Hedge: {basis['hedge_stance']}",
        f"ESP32: edge-filter 15%",
    ]
    _put_lines(canvas, lines, (480, 240 if esg["red_flag"] else 100))

    cv2.putText(
        canvas,
        "OrbitalBasis | Global Solution FIAP 2026.1",
        (24, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (100, 100, 100),
        1,
        cv2.LINE_AA,
    )

    out = ASSETS / filename
    cv2.imwrite(str(out), canvas)
    return out


def save_architecture_diagram() -> Path:
    w, h = 1400, 520
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 252

    cv2.putText(
        canvas,
        "OrbitalBasis — Arquitetura (Orbita + Campo + Mercado + IA)",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (14, 61, 92),
        2,
        cv2.LINE_AA,
    )

    boxes = [
        (40, 80, 200, 160, "Orbita", "NDVI OpenCV"),
        (260, 80, 200, 160, "Campo", "ESP32 edge"),
        (480, 80, 200, 160, "Mercado", "PTAX / B3"),
        (700, 80, 200, 160, "IA", "ESG + RAG + ML"),
        (920, 80, 220, 160, "Distribuido", "FastAPI + Streamlit"),
    ]
    for x, y, bw, bh, title, sub in boxes:
        cv2.rectangle(canvas, (x, y), (x + bw, y + bh), (14, 61, 92), 2)
        cv2.putText(canvas, title, (x + 12, y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (14, 61, 92), 2)
        cv2.putText(canvas, sub, (x + 12, y + 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1)

    orq_x, orq_y = 520, 300
    cv2.rectangle(canvas, (orq_x, orq_y), (orq_x + 280, orq_y + 70), (67, 160, 71), -1)
    cv2.putText(
        canvas,
        "OrbitalOrchestrator",
        (orq_x + 20, orq_y + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
    )

    for x, y, bw, bh, _, _ in boxes[:4]:
        cx, cy = x + bw // 2, y + bh
        cv2.arrowedLine(canvas, (cx, cy), (orq_x + 140, orq_y), (80, 80, 80), 2, tipLength=0.12)

    cv2.arrowedLine(canvas, (orq_x + 280, orq_y + 35), (920, 160), (80, 80, 80), 2, tipLength=0.08)

    out = ASSETS / "arquitetura_orbitalbasis.png"
    cv2.imwrite(str(out), canvas)
    return out


def save_esp32_diagram() -> Path:
    w, h = 1100, 380
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 250
    cv2.putText(
        canvas,
        "ESP32 field_node — Edge IoT (filtro 15% + janela horaria)",
        (24, 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (14, 61, 92),
        2,
    )

    nodes = [
        (40, 100, "Sensor solo", "GPIO34"),
        (280, 100, "ESP32", "media movel"),
        (520, 100, "MQTT", "anomalia"),
        (760, 100, "FastAPI", "/telemetry"),
        (980, 100, "Dashboard", "Streamlit"),
    ]
    for x, y, title, sub in nodes:
        cv2.rectangle(canvas, (x, y), (x + 180, y + 90), (14, 61, 92), 2)
        cv2.putText(canvas, title, (x + 10, y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (14, 61, 92), 2)
        cv2.putText(canvas, sub, (x + 10, y + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1)
        if x < 980:
            cv2.arrowedLine(canvas, (x + 180, y + 45), (x + 220, y + 45), (80, 80, 80), 2, tipLength=0.15)

    cv2.putText(
        canvas,
        "Firmware: src/hardware/esp32/field_node.ino",
        (24, h - 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (80, 80, 80),
        1,
    )
    out = ESP32_DIR / "iot_data_flow.png"
    cv2.imwrite(str(out), canvas)
    return out


def download_logo_fiap() -> Path | None:
    out = ASSETS / "logo-fiap.png"
    try:
        resp = requests.get(LOGO_URL, timeout=20)
        resp.raise_for_status()
        out.write_bytes(resp.content)
        return out
    except Exception as exc:
        print(f"Aviso: logo FIAP nao baixado ({exc})")
        return None


def main() -> None:
    _ensure_dirs()
    files = [
        save_ndvi_sample(),
        save_dashboard_composite(False, "dashboard_demo.png", "OrbitalBasis Dashboard — ESG OK"),
        save_dashboard_composite(True, "dashboard_esg_red_flag.png", "OrbitalBasis Dashboard — RED FLAG ESG"),
        save_architecture_diagram(),
        save_esp32_diagram(),
    ]
    logo = download_logo_fiap()
    if logo:
        files.append(logo)

    print("Assets gerados em assets/:")
    for path in files:
        print(f"  - {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
