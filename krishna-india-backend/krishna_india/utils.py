import os
import json
from pathlib import Path

import openai
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

HISTORY_DIR = Path(__file__).resolve().parent / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def get_openai_client() -> openai.OpenAI:
    """Create OpenAI client using environment variable."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return openai.OpenAI(api_key=api_key)

def configure_embedding():
    """Return embedding model used by the app."""
    return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def _history_path(session_id: str) -> Path:
    return HISTORY_DIR / f"{session_id}.json"

def load_history(session_id: str):
    path = _history_path(session_id)
    if path.exists():
        with path.open() as f:
            return json.load(f)
    return []

def append_history(session_id: str, role: str, content: str):
    history = load_history(session_id)
    history.append({"role": role, "content": content})
    with _history_path(session_id).open("w") as f:
        json.dump(history, f)
