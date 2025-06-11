from asyncio import sleep,create_task
from contextlib import asynccontextmanager
from datetime import datetime
from fasthtml.common import *
from random import random

app,rt = fast_app(exts='ws')

async def bg():
    while True:
        await send(Div(P(random()), id='dest', hx_swap_oob='beforeend'))
        await sleep(1)

async def life(o):
    create_task(bg())
    yield

send = app.setup_ws()
app.set_lifespan(life)

@rt
def index():
    return Titled("Random number broadcast station",
        Div(hx_ext='ws', ws_connect='/ws'),
        P(id='dest')
    )

serve()

