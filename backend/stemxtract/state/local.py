from stemxtract.state.base import (
    State,
    StateManager,
    TaskID,
    TaskParams,
    TaskState,
)

from typing import Dict, Optional
import asyncio

_ID_LENGTH = 12


# TODO: need to repesent file on-disk instead of in-memory
class LocalStateManager(StateManager):
    def __init__(self) -> None:
        self._state: Dict[TaskID, State] = {}

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

        raise NotImplementedError
