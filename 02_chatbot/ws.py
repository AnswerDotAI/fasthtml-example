from fasthtml.common import *
from claudette import *
import asyncio

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(tlink, dlink, picolink), ws_hdr=True)

# Set up a chat model client and list of messages (https://claudette.answer.ai/)
cli = Client(models[-1])
sp = """You are a helpful and concise assistant."""
messages = []

# Chat message component (renders a chat bubble)
def ChatMessage(msg):
    bubble_class = "chat-bubble-primary" if msg['role']=='user' else 'chat-bubble-secondary'
    chat_class = "chat-end" if msg['role']=='user' else 'chat-start'
    return Div(Div(msg['role'], cls="chat-header"),
               Div(msg['content'], cls=f"chat-bubble {bubble_class}"),
               cls=f"chat {chat_class}")

# The input field for the user message. Also used to clear the 
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(type="text", name='msg', id='msg-input', 
                 placeholder="Type a message", 
                 cls="input input-bordered w-full", hx_swap_oob='true')

# The main screen
@app.route("/")
def get():
    page = Body(H1('Chatbot Demo'),
                Div(*[ChatMessage(msg) for msg in messages],
                    id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
                    ws_send=True, hx_ext="ws", ws_connect="/wscon",
                    cls="flex space-x-2 mt-2",
                ), 
                cls="p-4 max-w-lg mx-auto",
                )
    return Title('Chatbot Demo'), page


@app.ws('/wscon')
async def ws(msg:str, send):

    # Send the user message to the user (updates the UI right away)
    messages.append({"role":"user", "content":msg.rstrip()})
    await send(Div(ChatMessage(messages[-1]), hx_swap_oob='beforeend', id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())

    # Simulate a delay
    await asyncio.sleep(1)

    # Get and send the model response
    r = cli(messages, sp=sp)
    messages.append({"role":"assistant", "content":contents(r)})
    await send(Div(ChatMessage(messages[-1]), hx_swap_oob='beforeend', id="chatlist"))

if __name__ == '__main__': uvicorn.run("ws:app", host='0.0.0.0', port=8000, reload=True)
