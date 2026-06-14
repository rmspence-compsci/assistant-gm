import os
import pytest


def test_settings_loads_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    import importlib
    import config.settings as s
    importlib.reload(s)
    assert s.ANTHROPIC_API_KEY == "test-key-123"


def test_settings_has_expected_constants(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    import importlib
    import config.settings as s
    importlib.reload(s)
    assert s.ANTHROPIC_MODEL == "claude-sonnet-4-6"
    assert s.CACHE_TTL_SECONDS == 3600
    assert s.PLAYER_CACHE_TTL_SECONDS == 604800
    assert s.NFL_SEASON == "2025"


def test_settings_raises_on_missing_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda **kwargs: None)
    import importlib
    import config.settings as s
    with pytest.raises(KeyError):
        importlib.reload(s)


def test_settings_loads_api_key_from_streamlit_secrets(monkeypatch):
    import sys, importlib
    from unittest.mock import MagicMock
    import config.settings as s
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda **kwargs: None)
    mock_st = MagicMock()
    mock_st.secrets.get.return_value = "streamlit-secret-key"
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    importlib.reload(s)
    assert s.ANTHROPIC_API_KEY == "streamlit-secret-key"


def test_settings_raises_when_key_missing_from_all_sources(monkeypatch):
    import sys, importlib
    from unittest.mock import MagicMock
    import config.settings as s
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda **kwargs: None)
    mock_st = MagicMock()
    mock_st.secrets.get.return_value = None
    monkeypatch.setitem(sys.modules, "streamlit", mock_st)
    with pytest.raises(KeyError):
        importlib.reload(s)


def test_settings_has_path_constants(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    import importlib
    import config.settings as s
    importlib.reload(s)
    from pathlib import Path
    assert isinstance(s.FINETUNE_LOG_PATH, Path)
    assert s.FINETUNE_LOG_PATH.name == "qa_log.jsonl"
