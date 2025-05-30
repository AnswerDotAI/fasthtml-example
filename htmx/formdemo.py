from fasthtml.common import *
app,rt = fast_app(live=True)

@rt
def submit(d:dict): return d

@rt
def index():
    return Titled('HTMX Form Demo', Grid(
        Form(hx_post=submit, hx_target="#result", hx_trigger="input delay:200ms")(
            Select(Option("One"), Option("Two"), id="select"),
            Input(value='j', type="text", id="name", placeholder="Name"),
            Input(value='h', type="text", id="email", placeholder="Email")),
        Button('Click me', hx_post=submit, hx_vals=dict(a=1,b=2), hx_target="#result"),
        Div(id="result")
    ))

serve()
