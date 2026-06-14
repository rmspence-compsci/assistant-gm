from auth.client import get_client


def sign_up(email: str, password: str):
    return get_client().auth.sign_up({"email": email, "password": password})


def sign_in(email: str, password: str):
    return get_client().auth.sign_in_with_password({"email": email, "password": password})


def sign_out() -> None:
    get_client().auth.sign_out()


def get_session():
    return get_client().auth.get_session()
