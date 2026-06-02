#!/usr/bin/env python3
"""Executa pipeline demo OrbitalBasis (terminal / vídeo)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core_logic.orchestrator import run_demo_analysis


def main() -> None:
    esg_demo = "--esg-red-flag" in sys.argv
    analysis = run_demo_analysis(esg_red_flag_demo=esg_demo)
    print("=== OrbitalBasis Demo ===\n")
    print("NDVI:", json.dumps(analysis.ndvi.summary, indent=2))
    print("\nESG:", analysis.esg_message)
    print("\nBasis:", json.dumps(analysis.basis.__dict__, default=str, indent=2))
    print("\nRAG context:", json.dumps(analysis.rag_context, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
