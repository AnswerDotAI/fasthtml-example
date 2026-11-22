from asyncio import sleep
from fasthtml.common import *
from random import random

app,rt = fast_app(exts='ws')

send = app.setup_ws()

@app.startup(bg=True)
async def bg():
    while True:
        await send(Div(P(random()), id='dest', hx_swap_oob='beforeend'))
        await sleep(1)


@rt
def index():
    return Titled("Random number broadcast station",
        Div(hx_ext='ws', ws_connect='/ws'),
        P(id='dest')
    )

serve()

