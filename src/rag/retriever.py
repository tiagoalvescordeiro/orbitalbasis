"""Retriever RAG — ChromaDB + consulta semântica."""

from __future__ import annotations

import logging
from typing import Any

from src.rag.indexer import ensure_index, get_chroma_collection

logger = logging.getLogger(__name__)


def retrieve_context(query: str, k: int = 4) -> list[dict[str, Any]]:
    try:
        ensure_index()
        collection = get_chroma_collection()
        result = collection.query(query_texts=[query], n_results=min(k, max(1, collection.count())))
        chunks: list[dict[str, Any]] = []
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        for doc, meta in zip(docs, metas):
            chunks.append({"content": doc, "source": (meta or {}).get("source", "unknown")})
        return chunks
    except Exception as exc:
        logger.warning("Retriever falhou: %s", exc)
        return []


def format_retrieved_chunks(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return ""
    return "\n\n".join(
        f"[{i}] ({c['source']})\n{c['content']}" for i, c in enumerate(chunks, 1)
    )
