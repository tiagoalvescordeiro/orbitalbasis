"""Fixtures compartilhadas — pytest OrbitalBasis."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolated_chroma_db(tmp_path, monkeypatch):
    """ChromaDB em diretório gravável (evita falha readonly no CI Linux)."""
    monkeypatch.setenv("ORBITAL_CHROMA_DIR", str(tmp_path / "chroma_db"))
