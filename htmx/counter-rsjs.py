from fasthtml.common import *
from utils import RsJs

app,rt = fast_app(live=True)

r = RsJs('incrementer')

def Incrementer(start=0, btn_txt='Increment'):
    return Section(r.d)(
        Output(start, r.output, id='my-output'),
        Button(btn_txt, r.increment)
    )

@rt("/")
def get():
    return Titled('RSJS Incrementer',
        r("htmx.on({increment}, 'click', _=>{output}.value++)"),
        Incrementer(),
        Incrementer(5, 'Do it')
    )

serve()

