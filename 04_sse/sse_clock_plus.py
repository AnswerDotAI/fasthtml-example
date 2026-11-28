"""This uses sse-starlette to better structure the SSE response."""
import asyncio
from datetime import datetime
from fasthtml.common import *
try:
    from sse_starlette.sse import EventSourceResponse
except ImportError:
    raise ImportError("Please install sse-starlette with 'pip install sse-starlette'")

app, rt = fast_app(exts='sse4')

@rt("/")
def get():
    return Titled("SSE Clock",
            Span(hx_sse_connect="/time-sender")(
                P("XX:XX")
            )
        )

async def time_generator():
    while True:
        # EventSourceResponse converts this dict to the proper format. Accepts
        # data, event, id, retry, comment keys
        # See https://github.com/sysid/sse-starlette/blob/main/sse_starlette/sse.py#L78-L94
        yield dict(
            # Maybe we can patch EventSourceResponse to run to_xml automatically if FT
            # components are detected in the data key, so we don't have to do it here
            # Note: For data, converts carriage returns to extra `data:` lines in the response
            data=to_xml(P(datetime.now().strftime('%H:%M:%S'))))
        await asyncio.sleep(1)

@rt("/time-sender")
async def get():
    "Send time to all connected clients every second"
    return EventSourceResponse(time_generator(), media_type="text/event-stream")

serve()
