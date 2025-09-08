from typing import List
from .config import load_settings
from .utils.logging import get_logger
from .agents.crawler_agent import run as crawl_run
from .agents.embedder_agent import run as embed_run
from .agents.retrieval_agent import retrieve
from .agents.analysis_agent import summarize
from .agents.notifier_agent import send_slack

logger = get_logger("orchestrator")

def run_ingest_pipeline() -> None:
    cnt = crawl_run()
    logger.info(f"Crawled {cnt} items")
    emb = embed_run()
    logger.info(f"Embedded {emb} chunks")

def run_digest(topics: List[str] = None) -> str:
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
