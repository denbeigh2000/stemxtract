from stemxtract.auth.oauth import OAuthAuthManager
from stemxtract.auth.oauth.token import AuthenticatedUser, TokenRecord
from stemxtract.views.auth import DISCORD_ID_SESSION_KEY, EXPIRY_SESSION_KEY
from datetime import datetime, timezone
from typing import Optional, Tuple

from dateutil.parser import parse as parse_datetime
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
)
from starlette.requests import HTTPConnection


class OAuthCredentials(AuthenticatedUser, AuthCredentials):
    def __init__(self, identity: str, token: TokenRecord) -> None:
        AuthCredentials.__init__(self, scopes=["authenticated"])
        AuthenticatedUser.__init__(self, identity, token)

    @classmethod
    def from_user(cls, user: AuthenticatedUser) -> "OAuthCredentials":
        return cls(user.identity, user.token)


# TODO: Should this be more decoupled from discord?
class DiscordUser(BaseUser):
    def __init__(self, discord_id: str):
        self.user_id = discord_id

        BaseUser.__init__(self)

    @property
    def display_name(self) -> str:
        return f"<unknown (user id: {self.user_id}>"

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def identity(self) -> str:
        return self.user_id


class DiscordAuthBackend(AuthenticationBackend):
    def __init__(self, auth_mgr: OAuthAuthManager) -> None:
        self._auth_mgr = auth_mgr

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple[OAuthCredentials, DiscordUser]]:
        now = datetime.now(timezone.utc)

        # NOTE: We trust here that the JWT signing guarantees that this id/expiry time
        # is correct
        discord_id: Optional[str] = conn.session.get(DISCORD_ID_SESSION_KEY)
        expires_raw: Optional[str] = conn.session.get(EXPIRY_SESSION_KEY)
        if not (discord_id and expires_raw):
            return None

        expires = parse_datetime(expires_raw)
        if now >= expires:
            return None

        user = DiscordUser(discord_id)
        # TODO: token should be fetched from a DB, refreshed if necessary
        record = await self._auth_mgr.fetch_token(discord_id)
        if not record:
            return None

        creds = OAuthCredentials(identity=discord_id, token=record)

        return (creds, user)
