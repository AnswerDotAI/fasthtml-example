from fasthtml.common import *

app,rt = fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    return Section(
        Button(btn_txt),
        Prev("me('output', m).value++;"),
        Output(start),
    )

@rt("/")
def get():
    return Titled(
        'Surreal Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it')
    )

serve()

