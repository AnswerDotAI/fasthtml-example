from fasthtml.common import *
app,rt = fast_app()

@rt("/")
def get():
    return Titled(
        'Hello',
        P('world'))

serve()

