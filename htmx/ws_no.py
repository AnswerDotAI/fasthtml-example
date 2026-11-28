from fasthtml.common import *

app, rt = fast_app()


@rt
def index():
    return Div(
        P(id="textid", name="textname", hx_post=handle, hx_target='#dest')(
            "Click Me"),
        P("Text to Update", id="dest"))

@rt
async def handle(hx_source:str): return Div(f"trigger: {hx_source}")

serve()

