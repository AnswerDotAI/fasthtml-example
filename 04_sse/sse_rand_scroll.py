import random
from asyncio import sleep
from fasthtml.common import *
from starlette.responses import StreamingResponse

hdrs=(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),)
app,rt = fast_app(hdrs=hdrs)

@rt
def index():
    return Titled("SSE Random Number Generator",
        P("Generate pairs of random numbers, as the list grows scroll downwards."),
        Div(hx_ext="sse", sse_connect="/number-stream",
            hx_swap="beforeend show:bottom", sse_swap="message"))

shutdown_event = signal_shutdown()
async def number_generator():
    while not shutdown_event.is_set():
        data = Div(
                Article(random.randint(1, 100)),
                Article(random.randint(1, 100)))
        yield sse_message(data)
        await sleep(1)

@rt("/number-stream")
async def get(): return EventStream(number_generator())
serve()

