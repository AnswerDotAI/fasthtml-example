from fasthtml.common import *
from claudette import *

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(tlink, dlink, picolink))

# Set up a chat model (https://claudette.answer.ai/)
chat = Chat(models[-1], sp="""You are a helpful and concise assistant.""")

# Chat message component (renders a chat bubble)
def ChatMessage(msg):
    text = msg['content'][0]['text'] if type(msg['content'][0]) == dict else msg['content'][0].text
    bubble_class = f"chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if msg['role'] == 'user' else 'start'}"
    return Div(Div(msg['role'], cls="chat-header"),
               Div(text, cls=f"chat-bubble {bubble_class}"),
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
    chat.h = [] # Clear the chat history on refresh
    page = Body(H1('Chatbot Demo'),
                Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
                    hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                    cls="flex space-x-2 mt-2",
                ), cls="doodle p-4 max-w-lg mx-auto")
    return Title('Chatbot Demo'), page

# Handle the form submission
@app.post("/")
def post(msg:str):
    chat(msg) # Send the message to the chat model
    return (ChatMessage(chat.h[-2]), # The user's message
            ChatMessage(chat.h[-1]), # The chatbot's response
            ChatInput()) # And clear the input field via an OOB swap


if __name__ == '__main__': uvicorn.run("basic:app", host='0.0.0.0', port=8000, reload=True)