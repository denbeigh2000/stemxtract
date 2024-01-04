from dataclasses import dataclass
from enum import Enum, IntEnum
import random
import string


_ID_LENGTH = 12


class TaskID(str):
    @classmethod
    def new_id(cls) -> "TaskID":
        return cls(
            "".join(
                random.choice(string.ascii_letters) for _ in range(_ID_LENGTH)
            )
        )


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
