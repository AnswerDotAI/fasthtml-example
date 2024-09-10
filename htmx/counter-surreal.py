from fasthtml.common import *

app,rt = fast_app(live=True)

def Incrementer(start=0, btn_txt='Increment'):
    scr = On('''
        let sec = e.closest('section');
        me('output', sec).value++;
    ''')
    return Section(
        Output(start),
        Button(btn_txt, scr))

@rt("/")
def get():
    return Titled('Surreal Incrementer',
        Incrementer(),
        Incrementer(5, 'Do it')
    )

serve()

