from stemxtract.task.base import TaskID, TaskParams, TaskState

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generator, Optional


class AuthToken(str):
    pass


@dataclass
class State:
    id: TaskID
    state: TaskState
    params: TaskParams


class StateManager(metaclass=ABCMeta):
    @abstractmethod
    async def create_task(
        self, params: TaskParams, token: AuthToken
    ) -> TaskID:
        ...

    @abstractmethod
    async def get_state(self, id: TaskID, token: AuthToken) -> Optional[State]:
        ...

    @abstractmethod
    async def get_results(
        self,
        id: TaskID,
        token: AuthToken,
    ) -> Optional[Generator[bytes, None, None]]:
        ...
