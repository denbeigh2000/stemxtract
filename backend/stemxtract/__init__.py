from stemxtract.auth.oauth import OAuthAuthManager
from stemxtract.auth.oauth.token import OAuthClientDetails, OAuthTokenURIs
from stemxtract.state.local import LocalStateManager
from stemxtract.views.auth import AuthView
from stemxtract.views.job import JobView

from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def TODO(request: Request):
    raise NotImplementedError()


async def homepage(request: Request):
    return JSONResponse({"hello": "world"})


# PLAN
#
# POST /xtract
# Download a song from a URL and extract the stems
# Creates and sets auth cookie if not present (to prevent others retrieving stems)
#
# GET /xtract/<id>/state
# Fetch the state of the process
# Requires an auth cookie that matches the one used for/awarded in the corresponding
# POST call
#
# GET /xtract/<id>/download
# Fetch the assets of a completed fetch/extract operation


async def TODO_id_func(token: str) -> str:
    raise NotImplementedError()


_DISCORD_API_BASE = "https://discord.com/api/v10"
_DISCORD_API_URIS = OAuthTokenURIs(
    user_auth=f"{_DISCORD_API_BASE}/oauth2/authorize",
    token_request=f"{_DISCORD_API_BASE}/oauth2/token",
    token_refresh=f"{_DISCORD_API_BASE}/oauth2/token",
    token_revoke=f"{_DISCORD_API_BASE}/oauth2/token/revoke",
    redirect="https://example.com/TODO",
)


def build_app() -> Starlette:
    client_info = OAuthClientDetails("TODO", "TODO")
    auth_mgr = OAuthAuthManager(
        TODO_id_func,
        client_info,
        _DISCORD_API_URIS,
    )
    auth_view = AuthView(auth_mgr)

    state_mgr = LocalStateManager(data_dir=Path("/tmp/stemxtract"))
    job_view = JobView(state_mgr)
    return Starlette(
        debug=True,
        routes=[
            Route("/auth/login", auth_view.login),
            Route("/auth/redirect", auth_view.redirect),
            Route("/xtract", job_view.create, methods=["POST"]),
            Route("/xtract/{id}/state", job_view.get),
            Route("/xtract/{id}/result", TODO),
            Route("/", homepage),
        ],
    )


app = build_app()
