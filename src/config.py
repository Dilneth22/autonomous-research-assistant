import os, yaml
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()

class ModelConfig(BaseModel):
    text: str = "gemini-1.5-flash"
    embedding: str = "models/text-embedding-004"

class Settings(BaseModel):
    topics: List[str]
    top_k: int = 8
    chunk_size: int = 1000
    chunk_overlap: int = 150
    vector_backend: str = os.getenv("VECTOR_BACKEND", "faiss")
    index_dir: str = os.getenv("INDEX_DIR", "./indexes")
    model: ModelConfig = ModelConfig()

def load_settings() -> Settings:
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    # Env substitutions
    vb = os.getenv("VECTOR_BACKEND", raw.get("vector_backend", "faiss"))
    idx = os.getenv("INDEX_DIR", raw.get("index_dir", "./indexes"))
    topics_env = os.getenv("TOPICS")
    topics = raw.get("topics", [])
    if topics_env:
        topics = [t.strip() for t in topics_env.split(",") if t.strip()]
    return Settings(
        topics=topics,
        top_k=raw.get("top_k", 8),
        chunk_size=raw.get("chunk_size", 1000),
        chunk_overlap=raw.get("chunk_overlap", 150),
        vector_backend=vb,
        index_dir=idx,
        model=ModelConfig(**raw.get("model", {}))
    )
