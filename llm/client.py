from collections.abc import Generator
import anthropic
from config import settings
from rag.prompts import SYSTEM_PROMPT

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def ask(question: str, context_str: str) -> str:
    content = f"{context_str}\n\nQUESTION: {question}" if context_str else question
    message = _client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    return message.content[0].text


def ask_stream(question: str, context_str: str) -> Generator[str, None, None]:
    content = f"{context_str}\n\nQUESTION: {question}" if context_str else question
    with _client.messages.stream(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    ) as stream:
        yield from stream.text_stream
