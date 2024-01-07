from stemxtract.state.base import State, TaskManager
from stemxtract.task.base import TaskID, TaskParams, TaskState

from http import HTTPStatus
import dataclasses
import mimetypes

from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse


class TaskView:
    def __init__(self, job_state_manager: TaskManager) -> None:
        self._state_mgr = job_state_manager

    @requires("authenticated")
    async def get(self, request: Request) -> JSONResponse:
        task_id = TaskID(request.path_params["id"])
        # TODO: This needs to also accept auth_header to verify ownership
        state = await self._state_mgr.get_state(task_id, "TODO")
        if not state:
            return JSONResponse(content=None, status_code=HTTPStatus.NOT_FOUND)

        return JSONResponse(content=dataclasses.asdict(state))

    @requires("authenticated")
    async def create(self, request: Request) -> JSONResponse:
        body = await request.json()
        params = TaskParams(**body)
        new_id = await self._state_mgr.create_task(params, "TODO")
        task = State(id=new_id, state=TaskState.CREATED, params=params)
        response = JSONResponse(dataclasses.asdict(task))

        return response

    @requires("authenticated")
    async def download(self, request: Request) -> Response:
        task_id = request.path_params["id"]
        result = await self._state_mgr.get_results(task_id, "TODO")
        if not result:
            return JSONResponse(content=None, status_code=HTTPStatus.NOT_FOUND)

        return StreamingResponse(
            result, media_type=mimetypes.types_map[".zip"]
        )
