from stemxtract.auth.oauth import OAuthAuthManager
from stemxtract.auth.oauth.token import OAuthClientDetails, OAuthTokenURIs
from stemxtract.auth.oauth.starlette import DiscordAuthBackend
from stemxtract.auth.oauth.discord import discord_identity
from stemxtract.state.local import LocalStateManager
from stemxtract.views.auth import AuthView
from stemxtract.views.task import TaskView

from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route


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
        discord_identity,
        client_info,
        _DISCORD_API_URIS,
    )
    auth_view = AuthView(auth_mgr)
    auth_backend = DiscordAuthBackend(auth_mgr)

    state_mgr = LocalStateManager(data_dir=Path("/tmp/stemxtract"))
    task_view = TaskView(state_mgr)
    return Starlette(
        debug=True,
        middleware=[
            # NOTE: developement settings only!
            Middleware(
                SessionMiddleware,
                secret_key="development",
                https_only=False,
            ),
            Middleware(AuthenticationMiddleware, backend=auth_backend),
        ],
        routes=[
            Route("/auth/login", auth_view.login),
            Route("/auth/redirect", auth_view.redirect),
            Route("/task", task_view.create, methods=["POST"]),
            Route("/task/{id}", task_view.get),
            Route("/task/{id}/download", task_view.download),
        ],
    )
