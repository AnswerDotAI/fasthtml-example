from fasthtml.common import *
from asyncio import sleep
from random import randint
import secrets

app,rt = fast_app()

def mk_row():
    idx = randint(0,1000)
    return Tr( Td(f'Agent {idx}'), Td(f'void{idx}@null.org'), Td(secrets.token_hex(8)))

def set_busy(b): return f"event.detail.elt.setAttribute('aria-busy', '{b}' )"

@rt('/')
def get():
    return Titled('Click load demo',
        PicoBusy(),
        P(I('Loading is delayed by 1 second to demonstrate use of "aria-busy" loading spinner in Pico.')),
        Table(
            Thead( Tr( Th('Name'), Th('Email'), Th('ID'))),
            Tbody( *[mk_row() for _ in range(5)], id='agents')),
        Button('Load Another Agent...',
               hx_get='/more', hx_target='#agents', hx_swap='beforeend', cls='btn primary')
    )

@rt('/more')
async def get():
    await sleep(1)
    return mk_row()

serve()

