from fasthtml.common import *

app,rt = fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    return Section(
        Output(start),
        Button(btn_txt),
        On("me('output', p).value++;"))

@rt("/")
def get():
    return Titled('Surreal Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it')
    )

serve()

