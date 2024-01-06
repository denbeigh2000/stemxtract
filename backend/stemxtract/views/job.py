from stemxtract.http import AUTH_COOKIE_HEADER, create_auth_cookie
from stemxtract.state.base import State, StateManager
from stemxtract.task.base import TaskID, TaskParams, TaskState

import dataclasses

from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse


class JobView:
    def __init__(self, job_state_manager: StateManager) -> None:
        self._state_mgr = job_state_manager

    @requires("authenticated", redirect="/login")
    async def get(self, request: Request) -> JSONResponse:
        task_id = TaskID(request.path_params["id"])
        auth_header = request.cookies.get(AUTH_COOKIE_HEADER)
        if not auth_header:
            return JSONResponse(content=None, status_code=403)

        # TODO: This needs to also accept auth_header to verify ownership
        state = await self._state_mgr.get_state(task_id, "TODO")
        if not state:
            return JSONResponse(content=None, status_code=404)

        return JSONResponse(content=dataclasses.asdict(state))

    @requires("authenticated", redirect="/login")
    async def create(self, request: Request) -> JSONResponse:
        auth_token = request.cookies.get(AUTH_COOKIE_HEADER)
        if not auth_token:
            auth_token = create_auth_cookie()

        body = await request.json()
        params = TaskParams(**body)
        new_id = await self._state_mgr.create_task(params, "TODO")
        task = State(id=new_id, state=TaskState.CREATED, params=params)
        response = JSONResponse(dataclasses.asdict(task))
        response.set_cookie(AUTH_COOKIE_HEADER, auth_token)

        return response
