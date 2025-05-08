from fasthtml.common import *

app,rt = fast_app()

@rt
def link():
    return (
        P('thing A'),
        P('thing B'),
        Div(P('thing C'), hx_swap_oob='afterend:#first'),
        Div(P('thing D'), hx_swap_oob='afterend:#first'),
        Div(P('thing E'), hx_swap_oob='afterend:#first'),
        Div(P('thing F'), hx_swap_oob='innerHTML', id='second'),
        Div(P('thing G'), hx_swap_oob='beforeend:#second'),
        Div(P('thing H'), hx_swap_oob='beforeend:#second'),
        Div(P('thing I'), hx_swap_oob='beforeend:#second'),
        P('thing J', hx_swap_oob='true', id='third'),
    )

@rt
def index():
    cts = (
        Button('click', hx_target='#first', hx_get=link, hx_swap='afterend'),
        Grid(
            Div( H3('first'),  Div(id='first' ) ),
            Div( H3('second'), Div(id='second') ),
            Div( H3('third'),  Div(id='third' ) )
        )
    )
    return Titled('HTMX swaps demo', *cts)

serve()

