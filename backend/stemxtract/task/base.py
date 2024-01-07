from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Generator, Optional

from stemxtract.util import random_id


_ID_LENGTH = 12


class TaskID(str):
    @classmethod
    def new_id(cls) -> "TaskID":
        return cls(random_id(_ID_LENGTH, include_nums=False))


class TaskState(IntEnum):
    CREATED = 1
    STARTED = 2
    FINISHED_SUCCESS = 3
    FINISHED_ERROR = 4
    FINISHED_LOST = 5


class Model(str, Enum):
    HTDEMUCS: str = "htdemucs"
    HTDEMUCS_FT: str = "htdemucs_ft"
    HTDEMUCS_6S: str = "htdemucs_6s"
    HTDEMUCS_MMI: str = "hdemucs_mmi"
    MDX: str = "mdx"
    MDX_EXTRA: str = "mdx_extra"
    MDX_Q: str = "mdx_q"
    MDX_EXTRA_Q: str = "mdx_extra_q"


@dataclass
class TaskParams:
    url: str
    model: Model = Model.HTDEMUCS


@dataclass
class Task:
    id: TaskID
    state: TaskState
    params: TaskParams


class TaskManager(metaclass=ABCMeta):
    @abstractmethod
    async def create_task(self, params: TaskParams, token: str) -> TaskID:
        ...

    @abstractmethod
    async def get_task(self, id: TaskID, token: str) -> Optional[Task]:
        ...

    @abstractmethod
    async def get_results(
        self,
        id: TaskID,
        token: str,
    ) -> Optional[Generator[bytes, None, None]]:
        ...
