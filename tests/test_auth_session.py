import importlib
from unittest.mock import MagicMock, patch


def _load_session(mock_client):
    import auth.session as session
    importlib.reload(session)
    session.get_client = lambda: mock_client
    return session


def test_sign_in_calls_supabase_with_credentials():
    mock_client = MagicMock()
    session = _load_session(mock_client)
    session.sign_in("test@example.com", "password123")
    mock_client.auth.sign_in_with_password.assert_called_once_with(
        {"email": "test@example.com", "password": "password123"}
    )


def test_sign_up_calls_supabase_with_credentials():
    mock_client = MagicMock()
    session = _load_session(mock_client)
    session.sign_up("new@example.com", "securepass")
    mock_client.auth.sign_up.assert_called_once_with(
        {"email": "new@example.com", "password": "securepass"}
    )


def test_sign_out_calls_supabase():
    mock_client = MagicMock()
    session = _load_session(mock_client)
    session.sign_out()
    mock_client.auth.sign_out.assert_called_once()


def test_get_session_returns_supabase_session():
    mock_client = MagicMock()
    mock_session = MagicMock()
    mock_client.auth.get_session.return_value = mock_session
    session = _load_session(mock_client)
    result = session.get_session()
    assert result is mock_session
