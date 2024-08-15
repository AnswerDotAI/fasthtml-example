"""Example from sse-starlette README https://github.com/sysid/sse-starlette/"""
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse


async def numbers(minimum, maximum):
    for i in range(minimum, maximum + 1):
        await asyncio.sleep(0.9)
        yield dict(data=i)


async def sse(request):
    generator = numbers(1, 5)
    return EventSourceResponse(generator)


routes = [Route("/", endpoint=sse)]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
