from typing import Dict
from ..utils.text import clean_text

def normalize_record(rec: Dict) -> Dict:
    return {
        "title": clean_text(rec.get("title", "")),
        "url": rec.get("url", ""),
        "published_at": rec.get("published_at", ""),
        "text": clean_text(rec.get("raw", "")),
    }
