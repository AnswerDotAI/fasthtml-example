from asyncio import sleep
from datetime import datetime
from fasthtml.common import *

app,rt = fast_app(exts='sse4')

@rt
def index():
    return Titled("SSE Clock",
        P("Display each second. As the display grows scroll downwards."),
        Div(hx_sse_connect="/time-sender", hx_swap="beforeend show:bottom")
    )

event = signal_shutdown()
async def time_generator():
    while not event.is_set():
        yield sse_message(Article(datetime.now().strftime('%H:%M:%S')))
        await sleep(1)

@rt("/time-sender")
async def get():
    "Send time to all connected clients every second"
    return EventStream(time_generator())

serve()

