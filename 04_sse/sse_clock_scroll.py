import asyncio
from datetime import datetime
from fasthtml.common import *
from starlette.responses import StreamingResponse

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
app, rt = fast_app(hdrs=(sselink,))

async def time_generator():
    while True:
        # We're considering adding capability in FastHTML to mirror the dict-style behavior in sse_starlette
        # which makes it easier to send multi-line data in the response
        # See https://github.com/sysid/sse-starlette/blob/main/sse_starlette/sse.py#L78-L94
        # In the meantime we submit the following as a single line of data
        yield f"event: TimeUpdateEvent\ndata: {to_xml(Article(datetime.now().strftime('%H:%M:%S')))}\n\n"
        # Also an idea is to patch StreamingResponse to run to_xml automatically if FT
        # components are detected in the data key, so we don't have to do it here
        # Note: For data, converts carriage returns to extra `data:` lines in the response
        await asyncio.sleep(1)

@rt
def index():
    return Titled("SSE Clock",
        P("Display each second. As the display grows scroll downwards."),
        Div(hx_ext="sse", sse_connect="/time-sender",
            hx_swap="beforeend show:bottom",
            sse_swap="TimeUpdateEvent")
    )

@rt("/time-sender")
async def get():
    "Send time to all connected clients every second"
    return StreamingResponse(time_generator(), media_type="text/event-stream")


serve()