from stemxtract.app import StemXtract
from stemxtract.http import AUTH_COOKIE_HEADER

from http import HTTPStatus
import mimetypes

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse


async def get_result(request: Request) -> Response:
    app: StemXtract = request.app

    auth_header = request.cookies.get(AUTH_COOKIE_HEADER)
    if not auth_header:
        return JSONResponse(content=None, status_code=HTTPStatus.FORBIDDEN)

    task_id = request.path_params["id"]
    result = app.manager.get_results(task_id)
    if not result:
        return JSONResponse(content=None, status_code=HTTPStatus.NOT_FOUND)

    return StreamingResponse(result, media_type=mimetypes.types_map[".zip"])
