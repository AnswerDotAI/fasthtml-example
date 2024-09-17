from fasthtml.common import *

app, rt = fast_app(ws_hdr=True)


@rt("/")
def get():
    return Div(
        P(ws_send=True, id="textid", name="textname", hx_ext="ws", ws_connect="/ws")(
            "Click Me"),
        P("Text to Update", id="dest")
    )


@app.ws("/ws")
async def ws(ws, send, hx_trigger:str):
    return Div(f"trigger: {hx_trigger}", id="dest", hx_swap_oob="true")

serve()

