import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent

ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
CACHE_TTL_SECONDS: int = 3600
PLAYER_CACHE_TTL_SECONDS: int = 604800
NFL_SEASON: str = "2025"
DB_PATH: Path = _ROOT / "data" / "league_cache.db"
FINETUNE_LOG_PATH: Path = _ROOT / "data" / "finetune" / "qa_log.jsonl"
