from stemxtract.app import StemXtract
from stemxtract.http import AUTH_COOKIE_HEADER
from stemxtract.task.base import TaskID

import dataclasses

from starlette.requests import Request
from starlette.responses import JSONResponse


async def get_job(request: Request) -> JSONResponse:
    task_id = TaskID(request.path_params["id"])
    auth_header = request.cookies.get(AUTH_COOKIE_HEADER)
    if not auth_header:
        return JSONResponse(content=None, status_code=403)

    app: StemXtract = request.app
    # TODO: This needs to also accept auth_header to verify ownership
    state = await app.manager.get_state(task_id)
    if not state:
        return JSONResponse(content=None, status_code=404)

    return JSONResponse(content=dataclasses.asdict(state))
