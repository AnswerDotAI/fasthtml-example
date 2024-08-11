from fasthtml.common import *
app,rt = fast_app()

@rt("/")
def get():
    return Titled('Hello',
        Safe('I fade <i>out</i> and <i>remove</i> my italics.'),
        Any('await sleep(1000); e.fadeOut()', 'i'),
        Div('Click me to remove me.', On('e.fadeOut()')),
        Button('Click me to remove me.', On('e.fadeOut()')),
        Div('I am leaving soon!'),
        Prev('await sleep(1000); e.fadeOut()')
    )

serve()
