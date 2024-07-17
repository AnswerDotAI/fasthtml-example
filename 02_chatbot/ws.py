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

# The input field for the user message. Also used to clear the 
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(type="text", name='msg', id='msg-input', 
                 placeholder="Type a message", 
                 cls="input input-bordered w-full", hx_swap_oob='true')

# The main screen
@app.route("/")
def get():
    global messages; messages = [] # Clear the chat history on refresh
    page = Body(H1('Chatbot Demo'),
                Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
                    hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                    cls="flex space-x-2 mt-2",
                ), 
                cls="doodle p-4 max-w-lg mx-auto",
                hx_ext="ws", ws_connect="/wscon")
    return Title('Chatbot Demo'), page

# Chat message component (renders a chat bubble)
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = f"chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if msg['role'] == 'user' else 'start'}"
    return Div(Div(msg['role'], cls="chat-header"),
               Div(msg['content'], cls=f"chat-bubble {bubble_class}"),
               cls=f"chat {chat_class}", id=f"chat-message-{msg_idx}", 
               **kwargs)

# Websockets
users = []
async def update(chat_message):
    for i, user_send in enumerate(users):
        try: await user_send(chat_message)
        except: users.pop(i)
async def on_connect(send): users.append(send)
async def on_disconnect(send): users.remove(send)

# Websocket route
@app.ws('/wscon', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str, send): pass

# Run the chat model in a separate thread
async def get_response(r, idx):
    for chunk in r: 
        messages[idx]["content"] += chunk
        await update(ChatMessage(idx, hx_swap_oob='true')) # Sends the latest version of the message to the client
        # PROBLEM: This does a ws update for every chunk, which is not ideal.

# Handle the form submission
@app.post("/")
def post(msg:str):
    idx = len(messages)
    messages.append({"role":"user", "content":msg})
    r = cli(messages, sp=sp, stream=True) # Send message to chat model (with streaming)
    messages.append({"role":"assistant", "content":""})
    asyncio.create_task(get_response(r, idx + 1))
    return (ChatMessage(idx), # The user's message
            ChatMessage(idx+1), # The chatbot's response
            ChatInput()) # And clear the input field via an OOB swap


if __name__ == '__main__': uvicorn.run("ws:app", host='0.0.0.0', port=8000, reload=True)