from fasthtml.common import *

app,rt = fast_app(hdrs=[HighlightJS()])

@rt("/convert")
def post(html: str): return Pre(Code(html2ft(html))) if html else ''

@rt("/")
def get():
    txt = Textarea(id="html", rows=10, hx_post='/convert', target_id="ft", hx_trigger='keyup delay:500ms'),
    return Titled("Convert HTML to FT",
                  Label("HTML"), txt, Div(id="ft"))

serve()

