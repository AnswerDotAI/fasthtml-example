from fasthtml.common import *

app, rt = fast_app(ws_hdr=True)


@rt
def index():
    return Div(
        P(id="textid", name="textname", hx_post=handle, hx_target='#dest')(
            "Click Me"),
        P("Text to Update", id="dest"))

@rt
async def handle(hx_trigger:str): return Div(f"trigger: {hx_trigger}")

serve()

