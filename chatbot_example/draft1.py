from starlette.responses import FileResponse
from fastcore.utils import *
from fasthtml import *
from cosette import *

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(tlink, dlink, picolink))

# Set up a chat model (using cosette, which is a wrapper around the openai api)
chat = Chat(models[0], sp="""You are a helpful and concise assistant.""")

# This is a container for the chat messages
def Chatbox(messages=()):
    """Add chat messages to this to see a nice chat history"""
    return Div(
        *[chat_message(msg) for msg in messages],
        cls="chat-box h-[73vh] overflow-y-auto", id="chatlist")

# And a single message, styled according to the role
def ChatMessage(text="", role="user", **kwargs):
    """A single message in a chat. Role 'user' on right, bots on the left."""
    # See https://daisyui.com/components/chat/
    bubble_class = f"chat-bubble-{'primary' if role == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if role == 'user' else 'start'}"
    return Div(
        Div(role, cls="chat-header"),
        Div(text, cls=f"chat-bubble {bubble_class}"),
        cls=f"chat {chat_class}", **kwargs)

# Convert a message from the chat model to a chat message component
def chat_message(msg):
    """Convert a message from the chat model to a chat message component"""
    msg = dict(msg)
    if type(msg['content']) == list: msg['content'] = msg['content'][0]['text']
    return ChatMessage(msg['content'], msg['role'])

# The main screen
@app.route("/")
def get():
    inp = Input(type="text", name='msg', id='msg-input', 
                  placeholder="Type a message", cls="input input-bordered w-full")
    page = Body(H1('Chatbot Demo'), Chatbox(),
                Form(Group(inp, Button("Send", cls="btn btn-primary")),
                    hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                    cls="flex space-x-2 mt-2",
                ), cls="doodle p-4 max-w-lg mx-auto") # Scary tailwind classes by GPT4o :)
    return Title('Chatbot Demo'), page

# Handle the form submission
@app.post("/")
async def post(request:Request):
    form_data = await request.form() # Get the data from the form
    chat(form_data['msg']) # Send the message to the chatbot, which adds it and the response to the chat history
    clear_chat_box = Input(type="text", name='msg', id='msg-input', placeholder="Type a message", 
                           cls="input input-bordered w-full", hx_swap_oob='true') # Clear the chat box
    return chat_message(chat.h[-2]), chat_message(chat.h[-1]), clear_chat_box # Return the last two messages and the chat box

if __name__ == '__main__':
  uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)