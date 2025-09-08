from typing import List, Dict, Any
from ..config import load_settings
from ..llm.gemini_client import summarize_with_context, get_text_model_name

def summarize(topic: str, docs: List[Dict[str, Any]]) -> str:
    settings = load_settings()
    model_name = get_text_model_name(settings.model.text)
    return summarize_with_context(model_name, topic, docs)
