from stemxtract.state.base import (
    State,
    StateManager,
)
from stemxtract.task.base import (
    TaskID,
    TaskParams,
    TaskState,
)

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple
import sys

from zipstream import AioZipStream  # type: ignore

_ID_LENGTH = 12


@dataclass
class ZipfileEntry:
    path: Path

    def __iter__(self) -> Generator[Tuple[str, str], None, None]:
        data = {
            "file": str(self.path.absolute()),
            "name": self.path.name,
        }

        return (_ for _ in data.items())


# TODO: need to repesent file on-disk instead of in-memory
class LocalStateManager(StateManager):
    def __init__(self, data_dir: Path) -> None:
        self._state: Dict[Tuple[str, TaskID], State] = {}
        self._data_dir = data_dir

    async def create_task(self, params: TaskParams, token: str) -> TaskID:
        new_id = TaskID.new_id()
        key = (token, new_id)
        while key in self._state:
            new_id = TaskID.new_id()
            key = (token, new_id)

        new_state = State(id=new_id, state=TaskState.CREATED, params=params)

        self._state[key] = new_state
        return new_id

    async def get_state(self, id: TaskID, token: str) -> Optional[State]:
        # TODO: This should check disk, etc
        key = (token, id)
        return self._state.get(key)

    async def get_results(
        self,
        id: TaskID,
        token: str,
    ) -> Optional[Generator[bytes, None, None]]:
        state = self._state.get((token, id))
        if state is None:
            return None

        if state.state != TaskState.FINISHED_SUCCESS:
            # TODO: improve
            raise RuntimeError("task state not in finished_success")

        model = state.params.model
        data_path = self._data_dir / id / str(model)

        if not data_path.exists():
            return None

        zip_paths = [
            dict(ZipfileEntry(path=item))
            for item in data_path.iterdir()
            if item.is_file()
        ]

        if not zip_paths:
            # TODO: Proper logging
            msg = f"WARN: Nothing under {data_path} (but directory exists)"
            print(msg, file=sys.stderr)
            return None

        # NOTE: Not 100% sure if this is accurate
        stream: Generator[bytes, None, None] = AioZipStream(zip_paths).stream()
        return stream
