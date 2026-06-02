import os

from src.rag.commercial_copilot import generate_briefing_markdown
from src.rag.indexer import build_chroma_index
from src.rag.retriever import retrieve_context


def test_build_chroma_index():
    n = build_chroma_index(force=True)
    assert n >= 3


def test_retrieve_context():
    build_chroma_index(force=True)
    chunks = retrieve_context("basis convergência contango", k=2)
    assert len(chunks) >= 1
    assert "content" in chunks[0]


def test_deterministic_briefing(monkeypatch):
    monkeypatch.setenv("ORBITAL_RAG_MODE", "deterministic")
    ctx = {
        "esg_compliant": True,
        "basis_atual": 4.3,
        "basis_indicativo": 4.5,
        "convergence_gap": 0.2,
        "curve_shape": "contango",
        "yield_risk_score": 40,
        "hedge_stance": "neutral",
        "basis_unit": "pontos",
        "narrative_hooks": [],
    }
    text = generate_briefing_markdown(ctx)
    assert "Briefing OrbitalBasis" in text
    assert "4.30" in text or "4.3" in text


def test_hybrid_briefing_includes_rag(monkeypatch):
    monkeypatch.setenv("ORBITAL_RAG_MODE", "hybrid")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    build_chroma_index(force=True)
    ctx = {
        "esg_compliant": True,
        "basis_atual": 3.0,
        "basis_indicativo": 4.0,
        "convergence_gap": 1.0,
        "curve_shape": "backwardation",
        "yield_risk_score": 70,
        "hedge_stance": "hedge_basis_mismatch_risk",
        "basis_unit": "pts",
        "narrative_hooks": ["test hook"],
    }
    text = generate_briefing_markdown(ctx)
    assert "Referências RAG" in text or "basis" in text.lower()
