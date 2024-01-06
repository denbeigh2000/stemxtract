from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Type,
    TypeVar,
    Union,
)
import sys

import aiohttp

from oauthlib.oauth2 import WebApplicationClient


_ZERO_TIME = timedelta()
_MIN_EXPIRY_TIME = timedelta(minutes=5)


E = TypeVar("E")


def _assert_type(arg: Any, typ: Type[E]) -> E:
    assert isinstance(arg, typ)
    return arg


@dataclass
class OAuthTokenURIs:
    user_auth: str
    token_request: str
    token_revoke: str

    redirect: str


@dataclass
class OAuthClientDetails:
    id: str
    secret: str


@dataclass
class RedirectCreds:
    code: str
    state: str


@dataclass
class TokenRecord:
    token: str
    refresh_token: str
    token_type: str
    expires_at: datetime
    scope: str

    @classmethod
    def from_raw(
        cls, data: Dict[str, Union[str, int]], now: Optional[datetime] = None
    ) -> "TokenRecord":
        now = now or datetime.now(timezone.utc)
        expiry = timedelta(seconds=float(data["expires_in"]))
        expires_at = now + expiry

        return cls(
            token=_assert_type(data["access_token"], str),
            refresh_token=_assert_type(data["refresh_token"], str),
            token_type=_assert_type(data["token_type"], str),
            expires_at=expires_at,
            scope=_assert_type(data["scope"], str),
        )

    def time_to_expiry(self, now: Optional[datetime] = None) -> timedelta:
        now = now or datetime.now(timezone.utc)
        remaining = self.expires_at - now

        return max(_ZERO_TIME, remaining)


@dataclass
class AuthenticatedUser:
    identity: str
    token: TokenRecord


class OAuthTokenStorage(ABC):
    @abstractmethod
    async def fetch(self, user_id: str) -> Optional[TokenRecord]:
        ...

    @abstractmethod
    async def upsert(self, user_id: str, record: TokenRecord) -> Optional[str]:
        ...

    @abstractmethod
    async def delete(self, token: str) -> None:
        ...


# IdentifyFn is an async function that takes a token, and returns a user id associated
# with that token
IdentifyFn = Callable[[str], Awaitable[str]]


class OAuthTokenManager:
    def __init__(
        self,
        id_func: IdentifyFn,
        client: OAuthClientDetails,
        storage: OAuthTokenStorage,
        uris: OAuthTokenURIs,
    ) -> None:
        self._id_func = id_func
        self._storage = storage
        self._client = WebApplicationClient(client.id, token=client.secret)
        self._uris = uris

    def auth_request_uri(self, scope: str, state: str) -> str:
        return self._client.prepare_request_uri(
            uri=self._uris.user_auth,
            redirect_uri=self._uris.redirect,
            state=state,
            scope=scope,
        )

    # NOTE: having this here is a little weird given the abstraction, but it feels
    # worthwhile to make use of this method
    def parse_response(self, uri: str) -> RedirectCreds:
        raw_data = self._client.parse_request_uri_response(uri=uri)
        return RedirectCreds(**raw_data)

    async def create(self, code: str, scope: str) -> AuthenticatedUser:
        (url, headers, body) = self._client.prepare_token_request(
            token_url=self._uris.token_request,
            authorization_response=code,
            redirect_url=self._uris.redirect,
            scope=scope,
        )
        data = body.encode("utf-8")

        raw_data: Dict[str, Union[str, int]]
        now: datetime
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as resp:
                now = datetime.now(timezone.utc)
                resp.raise_for_status()
                raw_data = await resp.json()

        record = TokenRecord.from_raw(raw_data, now)
        identity = await self._id_func(record.token)

        old_token = await self._storage.upsert(identity, record)
        if old_token:
            try:
                await self._revoke(old_token)
            except Exception as e:
                # TODO: better logging
                print(
                    f"WARN: Failed to revoke old token: {e}", file=sys.stderr
                )

        return AuthenticatedUser(identity, record)

    async def fetch(self, user_id: str) -> Optional[TokenRecord]:
        record = await self._storage.fetch(user_id)
        if not record:
            return None

        if record.time_to_expiry() < _MIN_EXPIRY_TIME:
            record = await self._refresh(user_id, record)

        return record

    async def _revoke(self, token: str) -> None:
        url, headers, body = self._client.prepare_token_revocation_request(
            self._uris.token_revoke,
            token,
        )
        data = body.encode("utf-8")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url, data=data, headers=headers
            ) as resp:
                resp.raise_for_status()

    async def _refresh(self, user_id: str, record: TokenRecord) -> TokenRecord:
        (url, headers, body) = self._client.prepare_refresh_token_request(
            self._uris.token_request, record.refresh_token, record.scope
        )

        data = body.encode("utf-8")
        new_record: TokenRecord
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as resp:
                now = datetime.now(timezone.utc)
                resp.raise_for_status()
                resp_data = await resp.json()
                new_record = TokenRecord.from_raw(resp_data, now)

        await self._storage.upsert(user_id, new_record)
        return new_record
