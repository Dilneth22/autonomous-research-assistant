from ..config import load_settings
from ..llm.gemini_client import embed_texts, get_embedding_model_name
from ..vectorstores.faiss_store import FaissStore
from ..vectorstores.lancedb_store import LanceDBStore

def _get_store(settings):
    if settings.vector_backend.lower() == "lancedb":
        return LanceDBStore(index_dir=settings.index_dir, dim=768)
    return FaissStore(index_dir=settings.index_dir, dim=768)

def retrieve(query: str, k: int = None):
    settings = load_settings()
    store = _get_store(settings)
    model_name = get_embedding_model_name(settings.model.embedding)
    qvec = embed_texts([query], model_name)[0]
    return store.search(qvec, k or settings.top_k)
