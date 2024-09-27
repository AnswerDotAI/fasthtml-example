from fasthtml import common as fh
from utils import Output,Button

app,rt = fh.fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    return fh.Section(
        fh.Style('me button {margin: 6px;}'),
        out := Output(start),
        Button(btn_txt, hx_on_click=f"{out}.value++")
    )

@rt("/")
def get():
    return fh.Titled('Uuid Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it'))

fh.serve()

