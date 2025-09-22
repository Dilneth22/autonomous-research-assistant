# Add these imports to the top of orchestrator.py
from typing import List
from .ingestion.loaders import fetch_article
from .utils.text import chunk_text
from .config import load_settings
from .llm.gemini_client import embed_texts, get_embedding_model_name
from .vectorstores.faiss_store import FaissStore
from .vectorstores.lancedb_store import LanceDBStore
from .agents.retrieval_agent import retrieve
from .agents.analysis_agent import summarize
from .agents.notifier_agent import send_slack
from .utils.logging import get_logger

logger = get_logger("orchestrator")

# This is a helper function to get the vector store, similar to the one in embedder_agent.py
def _get_store(settings):
    if settings.vector_backend.lower() == "lancedb":
        return LanceDBStore(index_dir=settings.index_dir, dim=768)
    return FaissStore(index_dir=settings.index_dir, dim=768)


# This is the new function you will add
def run_digest(topics: List[str] = None) -> str:
    """
    Generate a research digest for the given topics using the vector store.
    If no topics are provided, uses the topics from settings.
    """
    settings = load_settings()
    topics = topics or settings.topics
    all_sections = []
    for t in topics:
        docs = retrieve(t, k=settings.top_k)
        summary = summarize(t, docs)
        all_sections.append(f"*{t}*\n{summary}")
    digest = "\n\n".join(all_sections)
    send_slack(f"*Daily Research Digest*\n\n{digest}")
    return digest

def process_single_url(url: str) -> str:
    """
    Fetches, chunks, embeds, and stores the content from a single URL.
    """
    logger.info(f"Processing single URL: {url}")
    settings = load_settings()
    store = _get_store(settings)
    model_name = get_embedding_model_name(settings.model.embedding)

    # 1. Fetch the article content
    try:
        record = fetch_article(url)
        if not record.get("text"):
            raise ValueError("Could not extract text from the URL.")
    except Exception as e:
        logger.error(f"Failed to fetch or process URL {url}: {e}")
        raise e

    # 2. Chunk the text
    chunks = chunk_text(
        record["text"],
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # 3. Create metadata for each chunk
    metadatas = [{
        "title": record["title"],
        "url": record["url"],
        "text": chunk,
        "published_at": record.get("published_at", "")
    } for chunk in chunks]

    # 4. Embed the chunks
    logger.info(f"Embedding {len(chunks)} chunks for URL: {url}")
    embeddings = embed_texts(chunks, model_name)

    # 5. Upsert into the vector store
    if embeddings:
        store.upsert(embeddings, metadatas)
        logger.info(f"Successfully added {len(chunks)} chunks to the vector store.")
        return f"Successfully processed and added '{record['title']}' to the knowledge base."
    else:
        raise ValueError("Failed to generate embeddings for the content.")