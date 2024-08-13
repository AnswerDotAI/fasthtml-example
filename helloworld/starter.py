from random import random
from fasthtml.common import *
app,rt = fast_app()

@rt
def index():
    return Titled(
        'Hello',
        Div(P('click'), post=rnd)
    )

@rt
def rnd(): return P(random())

serve()

