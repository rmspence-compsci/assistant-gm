import importlib
from unittest.mock import MagicMock


def _load_module(mock_client):
    import storage.user_profile as up
    importlib.reload(up)
    up.get_client = lambda: mock_client
    return up


def test_get_profile_returns_data_for_existing_user():
    mock_client = MagicMock()
    expected = {"id": "user-123", "sleeper_username": "testuser"}
    (
        mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value
        .data
    ) = expected

    up = _load_module(mock_client)
    result = up.get_profile("user-123")

    assert result == expected
    mock_client.table.assert_called_with("user_profiles")


def test_get_profile_returns_none_when_no_profile():
    mock_client = MagicMock()
    (
        mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .maybe_single.return_value
        .execute.return_value
        .data
    ) = None

    up = _load_module(mock_client)
    result = up.get_profile("unknown-user")

    assert result is None


def test_upsert_profile_sends_user_id_and_sleeper_username():
    mock_client = MagicMock()

    up = _load_module(mock_client)
    up.upsert_profile("user-123", "sleeperuser")

    mock_client.table.assert_called_with("user_profiles")
    args = mock_client.table.return_value.upsert.call_args[0][0]
    assert args["id"] == "user-123"
    assert args["sleeper_username"] == "sleeperuser"
