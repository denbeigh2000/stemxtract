from stemxtract.app import StemXtract
from stemxtract.http import AUTH_COOKIE_HEADER, create_auth_cookie
from stemxtract.state.base import State, TaskParams, TaskState

from http.cookies import Morsel
import dataclasses

from starlette.requests import Request
from starlette.responses import JSONResponse


async def create_job(request: Request) -> JSONResponse:
    auth_token = request.cookies.get(AUTH_COOKIE_HEADER)
    if not auth_token:
        auth_token = create_auth_cookie()

    app: StemXtract = request.app

    body = await request.json()
    params = TaskParams(**body)
    new_id = await app.manager.create_task(params)
    task = State(id=new_id, state=TaskState.CREATED, params=params)
    response = JSONResponse(dataclasses.asdict(task))
    response.set_cookie(AUTH_COOKIE_HEADER, auth_token)

    return response
