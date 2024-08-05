from fasthtml.common import *
from random import randint
import secrets

app,rt = fast_app(live=True)

def mk_row():
    idx = randint(0,1000)
    return Tr( Td(f'Agent {idx}'), Td(f'void{idx}@null.org'), Td(secrets.token_hex(8)))

@rt('/')
def get():
    return (
        Table(
            Thead( Tr( Th('Name'), Th('Email'), Th('ID'))),
            Tbody(
                *[mk_row() for _ in range(5)],
            id='agents')),
        Button(
                'Load Another Agent...',
                hx_get='/more', hx_target='#agents', hx_swap='beforeend',
                cls='btn primary')
    )

@rt('/more')
def get(): return mk_row()

serve()
