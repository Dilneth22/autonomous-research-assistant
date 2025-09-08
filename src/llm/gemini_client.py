import os
import google.generativeai as genai
from typing import List, Dict, Any

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY, transport="rest")


def get_embedding_model_name(default: str) -> str:
    return os.getenv("GEMINI_EMBED_MODEL", default)

def get_text_model_name(default: str) -> str:
    return os.getenv("GEMINI_TEXT_MODEL", default)

def embed_texts(texts: List[str], model_name: str) -> List[List[float]]:
    # Uses the embeddings API; batches for simplicity
    out = []
    for t in texts:
        if not t:
            out.append([])
            continue
        resp = genai.embed_content(model=model_name, content=t)
        # Handle both legacy and current response shapes
        vec = None
        if isinstance(resp, dict) and "embedding" in resp:
            emb = resp["embedding"]
            if isinstance(emb, dict) and "values" in emb:
                vec = emb["values"]
            elif isinstance(emb, list):
                vec = emb
        elif hasattr(resp, "embedding"):
            emb = resp.embedding
            vec = getattr(emb, "values", emb)
        if not vec:
            vec = []
        out.append(vec)
    return out

def summarize_with_context(model_name: str, topic: str, snippets: List[Dict[str, Any]]) -> str:
    from google.generativeai import GenerativeModel
    system_msg = (
        "You are a concise research assistant. Summarize key developments as bullet points. "
        "Cite titles when helpful and avoid redundancy."
    )
    context_text = "\n\n".join([f"- {s.get('title','(untitled)')}: {s.get('text','')[:500]}" for s in snippets])
    prompt = f"""{system_msg}

    Topic: {topic}

    Source snippets:
    {context_text}

    Produce 5-10 compact bullet points with actionable insights.
    """
    model = GenerativeModel(model_name)
    resp = model.generate_content(prompt)
    return getattr(resp, "text", "").strip()
