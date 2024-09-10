from fasthtml.common import *
from fasthtml.svg import *

app,rt = fast_app(live=True)

def get_circle(val):
    if val: return G(hx_swap_oob='true', id='cts')(
        Circle(r=45, cx=50, cy=50, fill='red'),
        Circle(r=25, cx=70, cy=70, fill='green'))
    return Circle(id='cts', cx=50, cy=50, r=20, fill='blue',
        hx_swap_oob='true', hx_get=foo, hx_swap='outerHTML')

def get_btn(val):
    txt = 'Blue' if val else 'Multi',
    return Button(txt, hx_get=change, id='val', value=val, hx_swap_oob='true'),

@rt
def index():
    return Titled("HTMX SVG swaps",
        Svg(w=100, h=100)(
            get_circle(0),
            Rect(x=5, y=85, width=10, height=10, fill="purple")),
        get_btn(0))

@rt
def foo(): return SvgInb(Rect(x=50, y=50, width=30, height=30, fill='blue', id='cts'))

@rt
def change(val:int): return SvgOob(get_circle(1-val)), get_btn(1-val)

serve()

