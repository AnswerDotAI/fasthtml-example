"""Another pure FastHTML method, only dependency is python-fasthtml."""
import asyncio
import random
from fasthtml.common import *
from starlette.responses import StreamingResponse

app, rt = fast_app(exts='sse4')

@rt("/")
def get():
    return Titled("SSE Random Number Generator",
            Div("Random numbers coming...", hx_sse_connect="/number-stream"))

async def number_generator():
    "Generate a random number every second"
    while True:
        yield sse_message(Div(random.randint(1, 100)))
        await asyncio.sleep(1)

@rt("/number-stream")
async def get():
    "Send random numbers to all connected clients every second"
    return StreamingResponse(number_generator(), media_type="text/event-stream")

serve()
