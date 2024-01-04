from stemxtract.state.base import (
    State,
    StateManager,
    TaskID,
    TaskParams,
    TaskState,
)

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import asyncio
import dataclasses
import sys

from zipstream import AioZipStream

_ID_LENGTH = 12


@dataclass
class ZipfileEntry:
    path: Path
    name: str


# TODO: need to repesent file on-disk instead of in-memory
class LocalStateManager(StateManager):
    def __init__(self, data_dir: Path) -> None:
        self._state: Dict[TaskID, State] = {}
        self._data_dir = data_dir

    async def create_task(self, params: TaskParams) -> TaskID:
        while True:
            new_id = TaskID.new_id()
            if new_id in self._state:
                continue

            new_state = State(
                id=new_id, state=TaskState.CREATED, params=params
            )

            self._state[new_id] = new_state
            return new_id

    async def get_state(self, id: TaskID) -> Optional[State]:
        # TODO: This should check disk, etc
        return self._state.get(id)

    async def get_results(self, id: TaskID) -> Optional[asyncio.StreamReader]:
        state = self._state.get(id)
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
            dataclasses.asdict(ZipfileEntry(path=item, name=item.name))
            for item in data_path.iterdir()
            if item.is_file()
        ]

        if not zip_paths:
            # TODO: Proper logging
            print(f"WARN: No files found under ${data_path}", file=sys.stderr)
            return None

        return AioZipStream(zip_paths).stream()
