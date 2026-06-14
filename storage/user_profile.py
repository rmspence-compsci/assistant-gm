from auth.client import get_client


def get_profile(user_id: str) -> dict | None:
    res = (
        get_client()
        .table("user_profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return res.data if res is not None else None


def upsert_profile(user_id: str, sleeper_username: str) -> None:
    (
        get_client()
        .table("user_profiles")
        .upsert({"id": user_id, "sleeper_username": sleeper_username, "updated_at": "now()"})
        .execute()
    )
