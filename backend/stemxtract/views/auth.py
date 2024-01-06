from datetime import datetime, timedelta, timezone

from stemxtract.auth.oauth import OAuthAuthManager

from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse

DISCORD_ID_SESSION_KEY = "discord_id"
EXPIRY_SESSION_KEY = "login_expiry"

_SESSION_TIMEOUT = timedelta(days=90)


class AuthView:
    def __init__(self, auth_mgr: OAuthAuthManager) -> None:
        self._auth_mgr = auth_mgr

    async def login(self, request: Request) -> RedirectResponse:
        redirect_uri = await self._auth_mgr.handle_authorise()
        return RedirectResponse(
            url=redirect_uri,
            status_code=302,
        )

    async def redirect(self, request: Request) -> PlainTextResponse:
        url = str(request.url)
        # TODO: handle errors, invalid stuff, etc
        authenticated_user = await self._auth_mgr.handle_redirect(url)
        expiry_time = datetime.now(timezone.utc) + _SESSION_TIMEOUT
        request.session[DISCORD_ID_SESSION_KEY] = authenticated_user.identity
        request.session[EXPIRY_SESSION_KEY] = expiry_time.isoformat()
        return PlainTextResponse(content="OK")
