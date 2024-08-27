"""Another pure FastHTML method, only dependency is python-fasthtml."""
import asyncio
import random
from fasthtml.common import *
from starlette.responses import StreamingResponse

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
htmx_log = Script("htmx.logAll();"),
app, rt = fast_app(hdrs=(sselink,htmx_log))


@rt("/")
def get():
    return Titled("SSE Random Number Generator",
            Div(hx_trigger="from:#rando changed", hx_swap="afterend")(
                Div("Random numbers coming...", sse_swap="NumbersGeneratedEvent", id="rando", hx_ext="sse", sse_connect="/number-stream"))
            )

def Random():
    return Div(random.randint(1, 100), id="rando",  sse_swap="NumbersGeneratedEvent")

async def number_generator():
    "Generate a random number every second"
    while True:
        yield f"""event: NumbersGeneratedEvent\ndata: {to_xml(Random())}\n\n"""
        await asyncio.sleep(1)

@rt("/number-stream")
async def get():
    "Send random numbers to all connected clients every second"
    return StreamingResponse(number_generator(), media_type="text/event-stream")

serve()