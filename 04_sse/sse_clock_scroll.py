from asyncio import sleep
from datetime import datetime
from fasthtml.common import *

hdrs=(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),)
app,rt = fast_app(hdrs=hdrs)      

@rt
def index():
    return Titled("SSE Clock",
        P("Display each second. As the display grows scroll downwards."),
        Div(hx_ext="sse", sse_connect="/time-sender",
            hx_swap="beforeend show:bottom",
            sse_swap="message")
    )

shutdown_event = signal_shutdown()
async def time_generator():
    while not shutdown_event.is_set():
        data = Article(datetime.now().strftime('%H:%M:%S'))
        yield sse_message(data)
        await sleep(1)  

@rt("/time-sender")
async def get():
    "Send time to all connected clients every second"
    return EventStream(time_generator())


serve()