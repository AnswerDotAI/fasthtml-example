from fasthtml import common as fh
from utils import Output,Button

app,rt = fh.fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    out = Output(start)
    btn = Button(btn_txt, hx_on_click=f"{out}.value++")
    return fh.Section(out, btn)

@rt("/")
def get():
    return fh.Titled('Uuid Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it'))

fh.serve()

