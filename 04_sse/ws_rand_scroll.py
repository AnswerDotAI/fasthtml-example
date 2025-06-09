from asyncio import sleep,create_task
from datetime import datetime
from fasthtml.common import *
from random import random

async def bg():
    while True:
        await send(Div(P(random()), id='dest', hx_swap_oob='beforeend'))
        await sleep(1)

async def life(o):
    create_task(bg())
    yield

app,rt = fast_app(exts='ws', lifespan=life)
send = setup_ws(app)

@rt
def index():
    return Titled("Random number broadcast station",
        Div(hx_ext='ws', ws_connect='/ws'),
        P(id='dest')
    )

serve()

