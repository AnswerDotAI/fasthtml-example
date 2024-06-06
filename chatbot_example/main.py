from starlette.responses import FileResponse
from fastcore.utils import *
from fasthtml import *
from cosette import *

# Chat model
chat = Chat(models[0], sp="""You are the golden gate bridge. You love the golden gate bridge. You work factos about yourself into all chats.""")
messages = [
    {"role":"user", "content":"Hello!"},
    {"role":"assistant", "content":"Hello! How can I assist you today?"}
]

# Our FastHTML app
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(picolink, tlink, dlink))

def chat_message(msg_idx:int, stream: bool = False):
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
    

@app.get("/chat_message/{msg_idx}")
async def get_chat_message(msg_idx:int):
    if 'generating' in dict(messages[msg_idx]):
        return chat_message(msg_idx, stream=True)
    return chat_message(msg_idx)

# Main page
@app.get("/")
async def get():
    return Title('Chatbot Demo'), Main(
        H1('Chatbot Demo'), 
        Div(
            *[chat_message(i) for i, msg in enumerate(messages)],
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

@threaded
def get_response(r, idx):
    for chunk in r: messages[idx]['content'] += chunk
    print("Done", messages[idx])
    messages[idx] = {"role":"chatbot", "content":messages[idx]['content']}
    chat.h[-1] = {"role":"assistant", "content":messages[idx]['content']}

@app.post("/")
async def post(request:Request):
    form_data = await request.form()
    msg = form_data['msg']
    print("Hello", msg)
    clear_chat_box = Input(type="text", name='msg', id='msg-input', 
                           placeholder="Type a message", cls="input input-bordered w-full", 
                           hx_swap_oob='true')
    messages.append({'role':'user', 'content':msg})
    user_message = chat_message(len(messages)-1)
    r = chat(msg, stream=True)
    messages.append({'role':'chatbot', 'content':'', 'generating':True})
    bot_message = chat_message(len(messages)-1, stream=True)
    get_response(r, len(messages)-1) # Starts a new thread to fill in content
    return user_message, bot_message, clear_chat_box # User message and reset chatbox

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
async def static(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')