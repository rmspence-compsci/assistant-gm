from supabase import create_client, Client
from config import settings

_client: Client | None = None
_service_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _client


def get_service_client() -> Client:
    """Privileged client that bypasses RLS. For trusted backend jobs (the valuation
    pipeline) only — never expose SUPABASE_SERVICE_ROLE_KEY to the Streamlit app."""
    global _service_client
    if _service_client is None:
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "SUPABASE_SERVICE_ROLE_KEY is not set. The valuation pipeline needs it "
                "to write to Supabase. Add it to your .env file."
            )
        _service_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _service_client
