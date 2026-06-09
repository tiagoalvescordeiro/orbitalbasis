"""
Indexação ChromaDB (embeddings locais) para base de conhecimento OrbitalBasis.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "rag" / "knowledge"
COLLECTION_NAME = "orbitalbasis_knowledge"


def get_chroma_dir() -> Path:
    override = os.getenv("ORBITAL_CHROMA_DIR")
    if override:
        return Path(override)
    return PROJECT_ROOT / "data" / "chroma_db"


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]


def _load_documents() -> list[tuple[str, dict]]:
    docs: list[tuple[str, dict]] = []
    if not KNOWLEDGE_DIR.exists():
        return docs
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        docs.append((path.read_text(encoding="utf-8"), {"source": path.name}))
    return docs


def get_chroma_collection():
    import chromadb
    from chromadb.utils import embedding_functions

    chroma_dir = get_chroma_dir()
    chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_dir))
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def build_chroma_index(force: bool = False) -> int:
    """Indexa markdowns em ChromaDB. Retorna quantidade de chunks."""
    if force:
        import shutil

        shutil.rmtree(get_chroma_dir(), ignore_errors=True)

    collection = get_chroma_collection()
    if not force and collection.count() > 0:
        logger.info("Índice Chroma já existe (%d docs)", collection.count())
        return collection.count()

    raw = _load_documents()
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for text, meta in raw:
        for chunk in _chunk_text(text):
            ids.append(str(uuid.uuid4()))
            documents.append(chunk)
            metadatas.append(meta)

    if not documents:
        return 0

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    logger.info("Indexados %d chunks em %s", len(documents), get_chroma_dir())
    return len(documents)


def ensure_index() -> None:
    collection = get_chroma_collection()
    if collection.count() == 0:
        build_chroma_index(force=True)
