from fasthtml.common import *

'''
code = """
    me("[data-counter-output]", el).textContent++);
"""
scr = RsJsScript('counter', increment=('click', code))
'''

scr = Script('''
proc_htmx("[data-counter]", el => {
    me("[data-counter-increment]", el).on("click",
        e => me("[data-counter-output]", el).textContent++);
});''')

app,rt = fast_app(hdrs=(scr,), live=True)

def Incrementer(start=0, btn_txt='Increment'):
    return Section(data_counter=True)(
        Output(start, id='my-output', data_counter_output=True),
        Button(btn_txt, data_counter_increment=True))

@rt("/")
def get():
    return Titled('RSJS demo',
        Incrementer(),
        Incrementer(5, 'Do it')
    )

serve()

