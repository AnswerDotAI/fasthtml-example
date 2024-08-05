from fasthtml.common import *
app,rt = fast_app(live=True)

@rt('/')
def get():
    return Titled('HTMX Form Demo', Grid(
        Form(hx_post="/submit", hx_target="#result", hx_trigger="input delay:200ms")(
            Select(Option("One"), Option("Two"), id="select"),
            Input(value='j', type="text", id="name", placeholder="Name"),
            Input(value='h', type="text", id="email", placeholder="Email")),
        Div(id="result")
    ))

@rt('/submit')
def post(d:dict): return d

serve()
