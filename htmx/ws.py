from fasthtml.common import *

app, rt = fast_app(exts='ws')


@rt("/")
def get():
    return Div(
        P(hx_ws_send=True, id="textid", name="textname", hx_ws_connect="/ws")(
            "Click Me"),
        P("Text to Update", id="dest")
    )


@app.ws("/ws")
async def ws(ws, send, hx_source:str):
    return Div(f"trigger: {hx_source}", id="dest", hx_swap_oob="true")

serve()

