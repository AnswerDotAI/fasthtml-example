from fasthtml.common import *
from datetime import date

app,rt = fast_app(live=True)

@flexiclass
class MyForm: a:bool; dt:date

@rt("/")
def home():
    return (Form(Button("Submit"), hx_post="/process", hx_target='#result')(
        Input(name="a", type="checkbox"),
        Input(name="dt", type="date")),
    Div(id='result'))

@rt
def process(a: MyForm): return P(str(a))

serve()

