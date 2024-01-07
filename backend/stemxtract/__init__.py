from stemxtract.auth.oauth import OAuthAuthManager
from stemxtract.auth.oauth.token import OAuthClientDetails, OAuthTokenURIs
from stemxtract.auth.oauth.starlette import DiscordAuthBackend
from stemxtract.auth.oauth.discord import discord_identity
from stemxtract.task.base import TaskManager
from stemxtract.task.local import LocalTaskManager
from stemxtract.views.auth import AuthView
from stemxtract.views.task import TaskView

from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route
import click


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
    # NOTE: Should this live in this struct? needs to be configurable
    redirect="https://example.com/TODO",
)


def build_app(
    auth_mgr: OAuthAuthManager,
    task_mgr: TaskManager,
    client_info: OAuthClientDetails,
) -> Starlette:
    auth_view = AuthView(auth_mgr)
    auth_backend = DiscordAuthBackend(auth_mgr)

    task_view = TaskView(task_mgr)
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


def build_default_app() -> Starlette:
    client_info = OAuthClientDetails("TODO", "TODO")
    auth_mgr = OAuthAuthManager(
        discord_identity,
        client_info,
        _DISCORD_API_URIS,
    )
    task_mgr = LocalTaskManager(data_dir=Path("/tmp/stemxtract"))

    return build_app(auth_mgr, task_mgr, client_info)


@click.command(name="stemxtract")
@click.option(
    "--oauth-client-id", required=True, envvar="STEMXTRACT_OAUTH_CLIENT_ID"
)
@click.option(
    "--oauth-client-secret",
    required=True,
    envvar="STEMXTRACT_OAUTH_CLIENT_SECRET",
)
@click.option(
    "--data-dir",
    default="/tmp/stemxtract",
    envvar="STEMXTRACT_DATA_DIR",
    type=Path,
)
def main(
    oauth_client_id: str, oauth_client_secret: str, data_dir: Path
) -> None:
    client_info = OAuthClientDetails(oauth_client_id, oauth_client_secret)
    auth_mgr = OAuthAuthManager(
        discord_identity, client_info, _DISCORD_API_URIS
    )
    task_mgr = LocalTaskManager(data_dir)

    app = build_app(auth_mgr, task_mgr, client_info)

    import uvicorn

    uvicorn.run(app)


if __name__ == "__main__":
    main()
