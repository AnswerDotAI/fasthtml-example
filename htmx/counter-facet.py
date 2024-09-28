from fasthtml.common import *
from fasthtml.components import X_incrementer

facet = Script(src='https://cdn.jsdelivr.net/gh/kgscialdone/facet@0.1.2a/facet.min.js')
app,rt = fast_app(live=True, hdrs=[facet])

def Incrementer():
    return Template(component='x-incrementer')(
        Style('button {margin: 6px}'),
        Output(Slot() ),
        Button('Increment', Script("host.textContent++", on='click'))
    )

@rt
def index():
    return Titled('Web component counter',
        Incrementer(),
        X_incrementer('0'),
        X_incrementer('5'))

serve()

