from auth.client import get_client


def log_query(
    user_id: str,
    league_id: str,
    league_name: str,
    question: str,
    answer: str,
) -> None:
    (
        get_client()
        .table("query_logs")
        .insert({
            "user_id": user_id,
            "league_id": league_id,
            "league_name": league_name,
            "question": question,
            "answer": answer,
        })
        .execute()
    )
