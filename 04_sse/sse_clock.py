"""Pure FastHTML method, only dependency is python-fasthtml."""
import asyncio
from datetime import datetime
from fasthtml.common import *
from starlette.responses import StreamingResponse

app, rt = fast_app(exts='sse4')

@rt("/")
def get():
    return Titled("SSE Clock",
            P("XX:XX", hx_sse_connect="/time-sender"))

async def time_generator():
    while True:
        yield sse_message(P(datetime.now().strftime('%H:%M:%S')))
        await asyncio.sleep(1)

@rt("/time-sender")
async def get():
    "Send time to all connected clients every second"
    return StreamingResponse(time_generator(), media_type="text/event-stream")

serve()
