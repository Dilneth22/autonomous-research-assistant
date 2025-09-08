import yaml, json, os
from typing import List, Dict
from ..utils.logging import get_logger
from ..config import load_settings
from ..utils.text import clean_text
from ..ingestion.loaders import fetch_rss
logger = get_logger("crawler")

def run(output_path: str = "data/processed/records.jsonl") -> int:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open("src/ingestion/sources.yaml", "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f)
    rss_urls = sources.get("rss", [])
    items = fetch_rss(rss_urls, limit=15)
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for it in items:
            if not it.get("text"):
                continue
            it["text"] = clean_text(it["text"])
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            count += 1
    logger.info(f"Saved {count} normalized items to {output_path}")
    return count

if __name__ == "__main__":
    run()
