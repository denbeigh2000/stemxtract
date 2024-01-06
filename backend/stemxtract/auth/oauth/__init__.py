from typing import cast, Optional

from stemxtract.auth.oauth.state import (
    LocalOAuthStateStorage,
    OAuthStateManager,
    OAuthStateStorage,
)
from stemxtract.auth.oauth.token import (
    AuthenticatedUser,
    IdentifyFn,
    OAuthClientDetails,
    OAuthTokenManager,
    OAuthTokenStorage,
    OAuthTokenURIs,
    TokenRecord,
)

from oauthlib.oauth2 import WebApplicationClient
import aiohttp


class OAuthAuthManager:
    AUTHORISE_ENDPOINT: str
    TOKEN_ENDPOINT: str
    REVOKATION_ENDPOINT: str
    REDIRECT_ENDPOINT: str
    SCOPE: str

    def __init__(
        self,
        id_func: IdentifyFn,
        client_info: OAuthClientDetails,
        uris: OAuthTokenURIs,
        token_store: Optional[OAuthTokenStorage] = None,
        state_store: Optional[OAuthStateStorage] = None,
    ):
        if not state_store:
            state_store = LocalOAuthStateStorage()
        self._state_mgr = OAuthStateManager(state_store)
        # TODO: need to implement a real token store
        self._token_mgr = OAuthTokenManager(
            id_func, client_info, cast(OAuthTokenStorage, token_store), uris
        )

    async def handle_authorise(self) -> str:
        state = await self._state_mgr.add_state()
        return self._token_mgr.auth_request_uri(self.SCOPE, state)

    async def handle_redirect(self, uri: str) -> AuthenticatedUser:
        creds = self._token_mgr.parse_response(uri)

        if not self._state_mgr.validate_state(creds.state):
            # TODO: raise better error (and catch it upstream)
            raise RuntimeError("invalid state provided on redirect")

        user = await self._token_mgr.create(creds.code, self.SCOPE)

        return user

    async def fetch_token(self, user_id: str) -> Optional[TokenRecord]:
        return await self._token_mgr.fetch(user_id)
