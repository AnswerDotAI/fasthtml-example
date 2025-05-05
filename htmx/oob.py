from fasthtml.common import *
from asyncio import sleep
from random import randint
import secrets

app,rt = fast_app()

@rt
def link():
    return (
        P('thing A'),
        Div(P('thing B'), hx_swap_oob='afterend:#dest'),
        Div(P('thing C'), hx_swap_oob='afterend:#dest'),
        Div(P('thing D'), hx_swap_oob='afterend:#dest'),
        Div(P('thing E'), hx_swap_oob='innerHTML', id='dust'),
        P('thing E', hx_swap_oob='true', id='dust'),
    )

@rt
def index():
    cts = (
        Button('click', hx_target='#dest', hx_get=link, hx_swap='afterend'),
        P('dest'),
        Div(id='dest'),
        P('dust'),
        Div(id='dust'),
        P('dost'),
        Div(id='dost'),
    )
    return Titled('OOB demo', *cts)

serve()

