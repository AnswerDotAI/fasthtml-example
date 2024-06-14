from starlette.responses import FileResponse
from fastcore.utils import *
from fasthtml import *
from cosette import *
import uvicorn

# Chat model
chat = Chat(models[0], sp="""You are the golden gate bridge. 
You love the golden gate bridge. 
You work factos about yourself into all chats.""")

# Populate a few messages for testing appearance
messages = [
    {"role":"user", "content":"Hello!"},
    {"role":"assistant", "content":"Hello! How can I assist you today?"}
]

# Our FastHTML app
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(picolink, tlink, dlink))

# Chat message component (with streaming option)
def Message(msg_idx:int, stream: bool = False):
    """Create a single chat message component."""
    msg = dict(messages[msg_idx])
    print("M:", msg)
    if msg['role'] == 'user':
        return Div(
            Div('User',cls="chat-header"),
            Div(msg['content'], cls="chat-bubble chat-bubble-primary"),
            cls="chat chat-end", id=f"chat-message-{msg_idx}"
        )
    else: 
        if stream:
            return Div(
            Div('Chatbot',cls="chat-header"),
            Div(msg['content'], cls="chat-bubble chat-bubble-secondary"),
            cls="chat chat-start", id=f"chat-message-{msg_idx}",
            hx_trigger="every 0.1s", hx_swap="outerHTML", 
            hx_get=f"/chat_message/{msg_idx}"
        )
        return Div(
            Div('Chatbot',cls="chat-header"),
            Div(msg['content'], cls="chat-bubble chat-bubble-secondary"),
            cls="chat chat-start", id=f"chat-message-{msg_idx}"
        )
    
# Route that gets polled while streaming
@app.get("/chat_message/{msg_idx}")
def get_chat_message(msg_idx:int):
    if 'generating' in dict(messages[msg_idx]):
        return Message(msg_idx, stream=True)
    return Message(msg_idx)

# Main page
@app.get("/")
def get():
    return Title('Chatbot Demo'), Main(
        H1('Chatbot Demo'), 
        Div(
            *[Message(i) for i, msg in enumerate(messages)],
            cls="chat-box h-[80vh] overflow-y-auto", id="chatlist",
        ),
        Form(Group(
            Input(type="text", name='msg', id='msg-input', 
                  placeholder="Type a message", cls="input input-bordered w-full"),
            Button("Send", cls="btn btn-primary")),
            cls="flex space-x-2 mt-2",
            hx_post="/",
            hx_swap="beforeend",
            target_id="chatlist",
            hx_target="#chatlist"
        ),
        cls="p-4 max-w-lg mx-auto"
    )

# Run the chat model in a separate thread
@threaded
def get_response(r, idx):
    for chunk in r: messages[idx]['content'] += chunk
    messages[idx] = {"role":"chatbot", "content":messages[idx]['content']}
    chat.h[-1] = {"role":"assistant", "content":messages[idx]['content']}

# Get a message from the user and respond to it
@app.post("/")
async def post(request:Request):
    form_data = await request.form()
    msg = form_data['msg']
    clear_chat_box = Input(type="text", name='msg', id='msg-input', 
                           placeholder="Type a message", cls="input input-bordered w-full", 
                           hx_swap_oob='true')
    messages.append({'role':'user', 'content':msg})
    user_message = Message(len(messages)-1)
    r = chat(msg, stream=True)
    messages.append({'role':'chatbot', 'content':'', 'generating':True})
    bot_message = Message(len(messages)-1, stream=True)
    get_response(r, len(messages)-1) # Starts a new thread to fill in content
    return user_message, bot_message, clear_chat_box # User message and reset chatbox

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')

if __name__ == '__main__':
  uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)