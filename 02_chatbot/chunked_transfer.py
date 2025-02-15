from fasthtml.common import *
from claudette import *
from starlette.responses import StreamingResponse
import asyncio

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
hdrs = (picolink, tlink, dlink)

app = FastHTML(hdrs=hdrs, ct_hdr=True, cls="p-4 max-w-lg mx-auto", exts="chunked-transfer", live=True, debug=True)

@app.route("/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): 
    return FileResponse(f'{fname}.{ext}')

# Set up a chat model (https://claudette.answer.ai/)
cli = Client(models[-1])
sp = "You are a helpful and concise assistant."

def ChatMessage(msg, user: bool, id=None):
    bubble_class = "chat-bubble-primary" if user else "chat-bubble-secondary"
    chat_class = "chat-end" if user else "chat-start"
    return Div(cls=f"chat {chat_class}", id=f"msg-{id}")(
        Div("user" if user else "assistant", cls="chat-header"),
        Div(
            msg,
            cls=f"chat-bubble {bubble_class}",
            id=f"msg-{id}-content" if id else None,
        ),
        Hidden(
            msg,
            name="messages",
            id=f"msg-{id}-hidden" if id else None,
        ),
    )

# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(name='msg', id='msg-input', placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

# The main screen
@app.get
def index():
    page = Form(hx_post=send, hx_target="#chatlist", hx_swap="beforeend", hx_ext="chunked-transfer", hx_disabled_elt="#msg-group")(
            Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
            Div(cls="flex space-x-2 mt-2")(
                Group(ChatInput(), Button("Send", cls="btn btn-primary"), id="msg-group")
            )
           )
    return Titled('Chatbot Demo', page)

async def stream_response(msg, messages):
    yield to_xml(ChatMessage(msg, True, id=len(messages)-1))
    yield to_xml(ChatMessage('', False, id=len(messages)))
    r = (cli(messages, sp=sp, stream=True))
    response_txt = ''
    for chunk in r:
        response_txt += chunk
        yield to_xml(Div(
            response_txt,
            cls=f"chat-bubble chat-bubble-secondary",
            id=f"msg-{len(messages)}-content",
            hx_swap_oob="outerHTML",
        ))
        await asyncio.sleep(0.2)

    yield to_xml(Hidden(
        response_txt,
        name="messages",
        id=f"msg-{len(messages)}-hidden",
        hx_swap_oob="outerHTML",
    ))

    yield to_xml(ChatInput())

@app.post
async def send(msg:str, messages:list[str]=None):
    if not messages: messages = []
    messages.append(msg.rstrip())
    return StreamingResponse(stream_response(msg, messages), media_type="text/plain", headers={"X-Transfer-Encoding": "chunked"})

serve()
