from fasthtml.common import *
import utils

app,rt = fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    return Section(
        Style('me button {margin: 6px;}'),
        out := Output(start),
        Button(btn_txt, hx_on_click=f"{out}.value++")
    )

@rt("/")
def get():
    return Titled('Uuid Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it'))

serve()

