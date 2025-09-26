import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now import all required modules
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from urllib.parse import urlparse, urlencode
from email.utils import parsedate_to_datetime
import json, re, html
from datetime import datetime

from src.orchestrator import run_digest
from pydantic import BaseModel


app = FastAPI(title="Autonomous Research Assistant API")

# ---------- helpers ----------
def _parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except Exception:
        # Fallback: try ISO-ish strings
        try:
            return datetime.fromisoformat(s.replace("Z","").split(".")[0])
        except Exception:
            return None

def load_records(path: str = "data/processed/records.jsonl") -> List[Dict]:
    records: List[Dict] = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                rec["source"] = urlparse(rec.get("url", "")).netloc
                dt = _parse_dt(rec.get("published_at", ""))
                rec["_published_dt"] = dt
                rec["_published_key"] = dt.isoformat() if dt else ""
                # short snippet for display
                text = (rec.get("text") or "").strip()
                rec["_snippet"] = text[:600]
                records.append(rec)
            except Exception:
                continue
    return records

def sort_records(items: List[Dict], sort: str, order: str) -> List[Dict]:
    if sort == "title":
        key = lambda r: (r.get("title") or "").lower()
    elif sort == "source":
        key = lambda r: r.get("source") or ""
    else:  # default: published_at (use parsed dt when available)
        key = lambda r: r.get("_published_dt") or datetime.min
    reverse = (order.lower() == "desc")
    return sorted(items, key=key, reverse=reverse)

def _hl(s: str, q: Optional[str]) -> str:
    """Highlight query matches, keep output safe."""
    esc = html.escape(s or "")
    if not q:
        return esc
    pat = re.compile(re.escape(q), re.IGNORECASE)
    return pat.sub(lambda m: f"<mark>{m.group(0)}</mark>", esc)

def _fmt_dt(dt: Optional[datetime]) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""

def _page_link(base: str, **params) -> str:
    return f"{base}?{urlencode(params)}"

# ---------- existing endpoints ----------
@app.get("/health")
def health():
    return {"ok": True}





@app.get("/digest-preview")
def digest_preview():
    digest = run_digest()
    return {"digest": digest}

# ---------- JSON list ----------
@app.get("/articles")
def list_articles(
    q: Optional[str] = None,
    sort: str = Query("published_at", pattern="^(published_at|title|source)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    items = load_records()
    if q:
        ql = q.lower()
        items = [r for r in items if ql in (r.get("title","").lower() + " " + r.get("text","").lower())]
    items = sort_records(items, sort, order)
    total = len(items)
    items = items[offset:offset+limit]
    # trim heavy fields in JSON view
    for r in items:
        r["_snippet"] = r["_snippet"][:300]
        r["_published_dt"] = _fmt_dt(r.get("_published_dt"))
    return {"total": total, "limit": limit, "offset": offset, "items": items}

# ---------- HTML cards view (clean & readable) ----------
@app.get("/articles/html", response_class=HTMLResponse)
def list_articles_html(
    q: Optional[str] = None,
    sort: str = Query("published_at", pattern="^(published_at|title|source)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    base = "/articles/html"
    all_items = load_records()
    if q:
        ql = q.lower()
        all_items = [r for r in all_items if ql in (r.get("title","").lower() + " " + r.get("text","").lower())]
    all_items = sort_records(all_items, sort, order)
    total = len(all_items)
    items = all_items[offset:offset+limit]

    cards = []
    for r in items:
        title = r.get("title") or "(untitled)"
        url = r.get("url") or "#"
        src = r.get("source") or ""
        date = _fmt_dt(r.get("_published_dt"))
        snippet = r.get("_snippet") or ""
        if q:
            title_html = _hl(title, q)
            snippet_html = _hl(snippet, q)
        else:
            title_html = html.escape(title)
            snippet_html = html.escape(snippet)

        cards.append(f"""
        <article class="card">
          <div class="meta">
            <span class="date">{date}</span>
            <span class="source">{src}</span>
          </div>
          <h3 class="title"><a href="{html.escape(url)}" target="_blank" rel="noopener">{title_html}</a></h3>
          <p class="snippet">{snippet_html}</p>
        </article>
        """)

    # pagination links
    prev_link = ""
    next_link = ""
    if offset > 0:
        prev_link = f'<a class="btn" href="{_page_link(base, q=q or "", sort=sort, order=order, limit=limit, offset=max(0, offset - limit))}">« Prev</a>'
    if offset + limit < total:
        next_link = f'<a class="btn" href="{_page_link(base, q=q or "", sort=sort, order=order, limit=limit, offset=offset + limit)}">Next »</a>'

    html_page = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Collected Articles</title>
      <style>
        :root {{
          --bg:#0f172a; --card:#111827; --muted:#94a3b8; --text:#e5e7eb; --accent:#22d3ee;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 24px auto; max-width: 1100px; padding: 0 16px;
          background: var(--bg); color: var(--text); font: 15px/1.55 system-ui, -apple-system, Segoe UI, Roboto, Arial;
        }}
        header {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; }}
        header h1 {{ margin:0; font-size: 20px; }}
        header .muted {{ color: var(--muted); }}
        .controls {{ margin: 12px 0 16px; display:flex; gap:10px; flex-wrap:wrap; }}
        .controls a {{ color: var(--text); text-decoration:none; border:1px solid #334155; padding:6px 10px; border-radius:8px; }}
        .controls a.active {{ border-color: var(--accent); color: var(--accent); }}
        .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(320px,1fr)); gap:14px; }}
        .card {{ background: var(--card); border:1px solid #1f2937; border-radius:12px; padding:14px; }}
        .meta {{ color: var(--muted); font-size:12px; display:flex; gap:10px; }}
        .title {{ margin:8px 0 6px; font-size:16px; line-height:1.35; }}
        .title a {{ color: var(--text); text-decoration:none; }}
        .title a:hover {{ color: var(--accent); }}
        .snippet {{
          color: var(--muted);
          display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
          margin: 0;
        }}
        mark {{ background: #fde047; color:#111; padding:0 2px; border-radius:2px; }}
        .pager {{ display:flex; justify-content:space-between; margin-top:16px; }}
        .btn {{ color: var(--text); text-decoration:none; border:1px solid #334155; padding:6px 10px; border-radius:8px; }}
        .btn:hover {{ border-color: var(--accent); color: var(--accent); }}
      </style>
    </head>
    <body>
      <header>
        <h1>Collected Articles</h1>
        <span class="muted">Total: {total} • Showing {len(items)} (offset {offset})</span>
      </header>

      <div class="controls">
        <a href="{_page_link(base, q=q or '', sort='published_at', order='desc', limit=limit, offset=0)}" class="{'active' if sort=='published_at' and order=='desc' else ''}">Date ⬇</a>
        <a href="{_page_link(base, q=q or '', sort='published_at', order='asc', limit=limit, offset=0)}" class="{'active' if sort=='published_at' and order=='asc' else ''}">Date ⬆</a>
        <a href="{_page_link(base, q=q or '', sort='title', order='asc', limit=limit, offset=0)}" class="{'active' if sort=='title' else ''}">Title ⬆</a>
        <a href="{_page_link(base, q=q or '', sort='title', order='desc', limit=limit, offset=0)}" class="{'active' if sort=='title' else ''}">Title ⬇</a>
        <a href="{_page_link(base, q=q or '', sort='source', order='asc', limit=limit, offset=0)}" class="{'active' if sort=='source' else ''}">Source ⬆</a>
        <a href="{_page_link(base, q=q or '', sort='source', order='desc', limit=limit, offset=0)}" class="{'active' if sort=='source' else ''}">Source ⬇</a>
        <!-- Quick search links (or just use ?q=... in the URL) -->
        {f'<span class="muted">Search: ?q={html.escape(q)}</span>' if q else '<span class="muted">Tip: add ?q=keyword to filter</span>'}
      </div>

      <section class="grid">
        {''.join(cards)}
      </section>

      <div class="pager">
        <div>{prev_link}</div>
        <div>{next_link}</div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_page)
