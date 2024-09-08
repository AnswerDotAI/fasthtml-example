from fasthtml.common import *
from fasthtml.svg import *

app,rt = fast_app(live=True)

@rt
def index():
    return Titled("HTMX SVG swaps",
        Svg(w=100, h=100)(
            get_circle(0),
            Rect(x=5, y=85, width=10, height=10, fill="purple")),
        Hidden(id='ref', value='0'),
        Button('Multi', hx_get=change, hx_include='previous input'),
        Div(id='dest'),
    )

def get_circle(ref):
    opts = [
        Circle(id='circle1', cx=50, cy=50, r=20, fill='blue',
               hx_swap_oob='true', hx_get=foo, hx_swap='outerHTML'),
        G(hx_swap_oob='true', id='circle1')(
            Circle(r='45', cx='50', cy='50', fill='red'),
            Circle(r='25', cx='70', cy='70', fill='green')
        )
    ]
    return opts[ref]

@rt
def foo(): return SvgInb(Rect(x=50, y=50, width=30, height=30, fill='blue'))

@rt
def change(ref:int):
    return (
        'Multi' if ref else 'Blue',
        SvgOob(get_circle(1-ref)),
        Hidden(id='ref', value=1-ref, hx_swap_oob='true')
    )

serve()

