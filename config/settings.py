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
SUPABASE_SERVICE_ROLE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# Valuation pipeline
DP_BASE_URL = "https://raw.githubusercontent.com/dynastyprocess/data/master/files"
FFC_ADP_URL = "https://fantasyfootballcalculator.com/api/v1/adp/dynasty"
SLEEPER_TRENDING_URL = "https://api.sleeper.app/v1/players/nfl/trending/add"
FANTASYCALC_URL = "https://api.fantasycalc.com/values/current"
PIPELINE_FORMATS = ["1QB", "2QB"]
