"""Another pure FastHTML method, only dependency is python-fasthtml."""
import asyncio
import random
from fasthtml.common import *
from starlette.responses import StreamingResponse

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
app, rt = fast_app(hdrs=(sselink,))

@rt("/")
def get():
    return Titled("SSE Random Number Generator",
            Div("Random numbers coming...", sse_swap="NumbersGeneratedEvent", hx_ext="sse", sse_connect="/number-stream"))

async def number_generator():
    "Generate a random number every second"
    while True:
        yield f"""event: NumbersGeneratedEvent\ndata: {to_xml(Div(random.randint(1, 100), sse_swap="NumbersGeneratedEvent"))}\n\n"""
        await asyncio.sleep(1)

@rt("/number-stream")
async def get():
    "Send random numbers to all connected clients every second"
    return StreamingResponse(number_generator(), media_type="text/event-stream")

serve()