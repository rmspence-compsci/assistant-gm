import json
from pathlib import Path
from config import settings


def log_qa(question: str, context: str, answer: str) -> None:
    path = Path(settings.FINETUNE_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"question": question, "context": context, "answer": answer}
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
