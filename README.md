# Autonomous Research Assistant (Gemini + Local Vector DB)

Local-first pipeline that:
- Crawls selected sources (RSS / articles)
- Computes embeddings via **Gemini** API
- Stores vectors **locally** (FAISS or LanceDB)
- Runs RAG summaries via Gemini
- Delivers digests to Slack/email
- Optional Streamlit UI and FastAPI endpoints

## Quickstart

1. Create virtualenv and install deps
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env         # fill in keys
```

2. Configure topics & sources in `config/settings.yaml` and `src/ingestion/sources.yaml`

3. Run one-shot ingest + build index
```bash
python scripts/ingest_once.py
```

4. Generate a digest right now
```bash
python scripts/run_digest_now.py
```

5. (Optional) Start API & UI
```bash
uvicorn src.api.server:app --reload --port 8000
streamlit run src/ui/app.py
```

## Env Vars
Copy `.env.sample` to `.env` and populate values.

## Vector Backend
Choose `VECTOR_BACKEND=faiss` (default) or `lancedb` in `.env`.
