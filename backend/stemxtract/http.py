import random
import string

AUTH_COOKIE_HEADER = "StemXtract-Auth"
AUTH_COOKIE_LENGTH = 32


def create_auth_cookie() -> str:
    return "".join(
        random.choice(string.ascii_letters) for _ in range(AUTH_COOKIE_LENGTH)
    )
