from fasthtml.common import *
app,rt = fast_app()

@rt("/")
def get():
    return Titled(
        'Hello',
        NotStr('I fade <i>out</i> and <i>remove</i> my italics.'),
        Any('await sleep(100); e.fadeOut()', 'i')
    )

serve()
