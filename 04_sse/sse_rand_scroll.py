import random
from asyncio import sleep
from fasthtml.common import *

app,rt = fast_app(exts='sse4')

@rt
def index():
    return Titled("SSE Random Number Generator",
        P("Generate pairs of random numbers, as the list grows scroll downwards."),
        Div(hx_sse_connect="/number-stream", hx_swap="beforeend show:bottom"))

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

