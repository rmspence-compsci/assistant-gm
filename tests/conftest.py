import pytest
import importlib


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    import config.settings as s
    importlib.reload(s)
    monkeypatch.setattr(s, "DB_PATH", tmp_path / "test.db")
    import storage.cache as cache
    importlib.reload(cache)
    cache.init_db()
    return cache
