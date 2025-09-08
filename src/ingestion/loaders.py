from typing import List, Dict
import feedparser, requests
from newspaper import Article
from bs4 import BeautifulSoup
from .normalize import normalize_record

def fetch_rss(urls: List[str], limit: int = 10) -> List[Dict]:
    items = []
    for u in urls:
        feed = feedparser.parse(u)
        for entry in feed.entries[:limit]:
            rec = {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "published_at": entry.get("published", ""),
                "raw": entry.get("summary", ""),
            }
            items.append(normalize_record(rec))
    return items

def fetch_article(url: str) -> Dict:
    art = Article(url)
    art.download(); art.parse()
    rec = {"title": art.title, "url": url, "published_at": str(art.publish_date or ""), "raw": art.text}
    return normalize_record(rec)

def fetch_url_text(url: str) -> str:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.get_text(" ", strip=True)
