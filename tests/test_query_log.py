import importlib
from unittest.mock import MagicMock


def _load_module(mock_client):
    import storage.query_log as ql
    importlib.reload(ql)
    ql.get_client = lambda: mock_client
    return ql


def test_log_query_inserts_all_fields_to_supabase():
    mock_client = MagicMock()

    ql = _load_module(mock_client)
    ql.log_query(
        user_id="user-123",
        league_id="league-456",
        league_name="Test League",
        question="Who should I start?",
        answer="Start Player A.",
    )

    mock_client.table.assert_called_with("query_logs")
    args = mock_client.table.return_value.insert.call_args[0][0]
    assert args["user_id"] == "user-123"
    assert args["league_id"] == "league-456"
    assert args["league_name"] == "Test League"
    assert args["question"] == "Who should I start?"
    assert args["answer"] == "Start Player A."


def test_log_query_calls_execute():
    mock_client = MagicMock()

    ql = _load_module(mock_client)
    ql.log_query("u", "l", "League", "Q", "A")

    mock_client.table.return_value.insert.return_value.execute.assert_called_once()
