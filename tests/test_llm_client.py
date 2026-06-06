from unittest.mock import MagicMock, patch


@patch("llm.client._client")
def test_ask_returns_text(mock_client):
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Start Jefferson.")]
    mock_client.messages.create.return_value = mock_message

    from llm.client import ask
    result = ask("Who should I start?", "LEAGUE: Test League\nYOUR STARTERS: Jefferson")
    assert result == "Start Jefferson."
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["model"] == "claude-sonnet-4-6"
    assert "fantasy football" in call_kwargs["system"].lower()


@patch("llm.client._client")
def test_ask_includes_context_in_message(mock_client):
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Answer.")]
    mock_client.messages.create.return_value = mock_message

    from llm.client import ask
    ask("My question", "Some context")
    messages = mock_client.messages.create.call_args[1]["messages"]
    assert "Some context" in messages[0]["content"]
    assert "My question" in messages[0]["content"]
