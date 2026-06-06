import json
from pathlib import Path
import importlib


def test_log_qa_creates_file_and_appends(tmp_path, monkeypatch):
    log_path = tmp_path / "finetune" / "qa_log.jsonl"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    import config.settings as s
    importlib.reload(s)
    monkeypatch.setattr(s, "FINETUNE_LOG_PATH", log_path)
    import storage.finetune_log as fl
    importlib.reload(fl)

    fl.log_qa("What should I start?", "context here", "Start Player A.")
    fl.log_qa("Who to drop?", "context 2", "Drop Player B.")

    lines = Path(log_path).read_text().strip().split("\n")
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry["question"] == "What should I start?"
    assert entry["context"] == "context here"
    assert entry["answer"] == "Start Player A."
