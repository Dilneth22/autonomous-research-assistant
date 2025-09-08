import json, os
from typing import List, Dict
from ..utils.logging import get_logger
from ..utils.text import chunk_text
from ..config import load_settings
from ..llm.gemini_client import embed_texts, get_embedding_model_name
from ..vectorstores.faiss_store import FaissStore
from ..vectorstores.lancedb_store import LanceDBStore

logger = get_logger("embedder")

def _get_store(settings):
    if settings.vector_backend.lower() == "lancedb":
        return LanceDBStore(index_dir=settings.index_dir, dim=768)
    return FaissStore(index_dir=settings.index_dir, dim=768)

def run(input_path: str = "data/processed/records.jsonl") -> int:
    settings = load_settings()
    store = _get_store(settings)
    model_name = get_embedding_model_name(settings.model.embedding)

    texts, metas = [], []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            chunks = chunk_text(rec["text"], chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
            for ch in chunks:
                texts.append(ch)
                metas.append({"title": rec["title"], "url": rec["url"], "text": ch, "published_at": rec["published_at"]})

    logger.info(f"Embedding {len(texts)} chunks with {model_name} ...")
    embs = embed_texts(texts, model_name)
    # Filter out empty embeddings
    filtered = [(e, m) for e, m in zip(embs, metas) if e]
    if not filtered:
        logger.warning("No embeddings produced; check API key or model name.")
        return 0
    embs2, metas2 = zip(*filtered)
    store.upsert(list(embs2), list(metas2))
    logger.info(f"Index stats: {store.stats()}")
    return len(embs2)

if __name__ == "__main__":
    run()
