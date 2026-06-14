import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent

try:
    import streamlit as st
    _key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
except Exception:
    _key = os.environ.get("ANTHROPIC_API_KEY", "")
if not _key:
    raise KeyError("ANTHROPIC_API_KEY")
ANTHROPIC_API_KEY: str = _key
ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
CACHE_TTL_SECONDS: int = 3600
PLAYER_CACHE_TTL_SECONDS: int = 604800
NFL_SEASON: str = "2025"
FINETUNE_LOG_PATH: Path = _ROOT / "data" / "finetune" / "qa_log.jsonl"
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")
