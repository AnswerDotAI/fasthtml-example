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
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = f"chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if msg['role'] == 'user' else 'start'}"
    return Div(Div(msg['role'], cls="chat-header"),
               Div(msg['content'], 
                   id=f"chat-content-{msg_idx}", # Target if updating the content
                   cls=f"chat-bubble {bubble_class}"),
               id=f"chat-message-{msg_idx}", # Target if replacing the whole message
               cls=f"chat {chat_class}", **kwargs)

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
                    hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                    cls="flex space-x-2 mt-2",
                ), 
                cls="doodle p-4 max-w-lg mx-auto",
                hx_ext="ws", ws_connect="/wscon") # Open a websocket connection on page load
    return Title('Chatbot Demo'), page



open_websocket_sends = set()

async def update(chat_message):
    to_remove = []
    for send in open_websocket_sends:
        try: await send(chat_message)
        except: to_remove.append(send)
    for send in to_remove:
        open_websocket_sends.remove(send)

async def on_connect(send): open_websocket_sends.add(send)

async def on_disconnect(send): open_websocket_sends.discard(send)

@app.ws('/wscon', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str, send, request): 
    # This function runs when a message is received on the websocket,
    # which we don't need to handle in this example. Instead, we keep track
    # of the send function so that we can send messages to the client
    pass

# Run the chat model in a separate thread
async def get_response(idx):

    # Non-streaming:
    # r = cli(messages[:idx], sp=sp) # Send past messages to chat model
    # messages[idx]["content"] = contents(r) # Get response from chat model
    # await update(ChatMessage(idx, hx_swap_oob='true')) # Update in the UI

    # Streaming:
    r = cli(messages[:idx], sp=sp, stream=True) # Send past messages to chat model
    for chunk in r: 
        messages[idx]["content"] += chunk

        # Option 1: Update the whole message each chunk
        # await update(ChatMessage(idx, hx_swap_oob='true'))

        # Option 2: Add new chunks to the content as they come in
        await update(Span(chunk, id=f"chat-content-{idx}", hx_swap_oob="beforeend"))

        # Add this to test coping with a delay: await asyncio.sleep(0.5)

# Handle the form submission
@app.post("/")
def post(msg:str):
    idx = len(messages)
    messages.append({"role":"user", "content":msg})
    messages.append({"role":"assistant", "content":""}) # Response initially blank
    asyncio.create_task(get_response(idx+1)) # Start a task that will update the chat message
    return (ChatMessage(idx), # The user's message
            ChatMessage(idx+1), # The chatbot's response
            ChatInput()) # And clear the input field via an OOB swap


if __name__ == '__main__': uvicorn.run("ws:app", host='0.0.0.0', port=8000, reload=True)