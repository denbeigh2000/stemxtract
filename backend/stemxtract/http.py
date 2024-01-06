from stemxtract.util import random_id

AUTH_COOKIE_HEADER = "StemXtract-Auth"
AUTH_COOKIE_LENGTH = 32


def create_auth_cookie() -> str:
    return random_id(AUTH_COOKIE_LENGTH)
