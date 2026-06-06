from rag.prompts import SYSTEM_PROMPT


def test_system_prompt_mentions_fantasy_football():
    assert "fantasy football" in SYSTEM_PROMPT.lower()


def test_system_prompt_has_guardrail():
    assert "unrelated" in SYSTEM_PROMPT.lower() or "decline" in SYSTEM_PROMPT.lower()
