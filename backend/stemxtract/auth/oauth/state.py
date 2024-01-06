from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Optional

from stemxtract.util import random_id


class OAuthStateStorage(ABC):
    @abstractmethod
    async def insert(self, state: str, timestamp: datetime) -> None:
        ...

    @abstractmethod
    async def contains(self, state: str) -> bool:
        ...

    @abstractmethod
    async def pop(self, state: str) -> Optional[datetime]:
        ...


# TODO: Proper state storage
class LocalOAuthStateStorage(OAuthStateStorage):
    def __init__(self):
        self._store = {}

    async def insert(self, state: str, timestamp: datetime) -> None:
        assert state not in self._store, "state exists"
        self._store[state] = timestamp

    async def contains(self, state: str) -> bool:
        return state in self._store

    async def pop(self, state: str) -> Optional[datetime]:
        return self._store.pop(state)


class OAuthStateManager:
    _MAX_ALLOWABLE_STATE_TIME = timedelta(minutes=5)
    _ID_LENGTH = 32

    def __init__(self, storage: OAuthStateStorage) -> None:
        self._store = storage

    @classmethod
    def _new_random_id(cls) -> str:
        return random_id(cls._ID_LENGTH)

    async def add_state(self) -> str:
        new_id = self._new_random_id()
        now = datetime.now(timezone.utc)
        while self._store.contains(new_id):
            new_id = self._new_random_id()

        await self._store.insert(new_id, now)
        return new_id

    async def validate_state(self, state: str) -> bool:
        now = datetime.now(timezone.utc)
        created_at = await self._store.pop(state)
        if not created_at:
            return False

        age = now - created_at
        if age > self._MAX_ALLOWABLE_STATE_TIME:
            # time between creation and state re-use is too long
            return False

        # The state exists, is fresh and has been removed from the store.
        return True
