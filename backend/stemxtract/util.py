import secrets
import string

_ALNUM = string.ascii_letters + string.digits


def random_id(n: int, include_nums: bool = True) -> str:
    chrset = _ALNUM if include_nums else string.ascii_letters
    return "".join(secrets.choice(chrset) for _ in range(n))
