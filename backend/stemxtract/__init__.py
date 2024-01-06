from stemxtract.app import StemXtract

from stemxtract.views.create_job import create_job
from stemxtract.views.get_job import get_job

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def TODO(request: Request):
    raise NotImplementedError()


async def homepage(request: Request):
    return JSONResponse({"hello": "world"})


# PLAN
#
# POST /xtract
# Download a song from a URL and extract the stems
# Creates and sets auth cookie if not present (to prevent others retrieving stems)
#
# GET /xtract/<id>/state
# Fetch the state of the process
# Requires an auth cookie that matches the one used for/awarded in the corresponding
# POST call
#
# GET /xtract/<id>/download
# Fetch the assets of a completed fetch/extract operation

app = StemXtract(
    debug=True,
    routes=[
        Route("/xtract", create_job, methods=["POST"]),
        Route("/xtract/{id}/state", get_job),
        Route("/xtract/{id}/result", TODO),
        Route("/", homepage),
    ],
)
