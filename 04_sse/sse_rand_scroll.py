import asyncio, random
from fasthtml.common import *
from starlette.responses import StreamingResponse

app, rt = fast_app(hdrs=(Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),))

@rt
def index():
    return Titled("SSE Random Number Generator",
        P("Generate a random number, as the list grows scroll downwards."),
        Div(hx_ext="sse", sse_connect="/number-stream",
            hx_swap="beforeend show:bottom",
            sse_swap="NumbersGeneratedEvent")
    )

def Random(): return Article(random.randint(1, 100))

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