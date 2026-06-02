#!/usr/bin/env python3
"""Constrói índice ChromaDB da base de conhecimento."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.indexer import build_chroma_index


def main() -> None:
    force = "--force" in sys.argv
    n = build_chroma_index(force=force)
    print(f"OrbitalBasis RAG: {n} chunks indexados.")


if __name__ == "__main__":
    main()
