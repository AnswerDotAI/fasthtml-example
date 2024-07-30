from fasthtml.common import *
import os
from openai import OpenAI

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com")
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(tlink, dlink, picolink))

# Initialize the OpenAI client
# openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4o-mini"  # model = "gpt-3.5-turbo"
sp = "You are a helpful and concise assistant."
messages = []

# Chat message component (renders a chat bubble)
def ChatMessage(msg):
    bubble_class = f"chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if msg['role'] == 'user' else 'start'}"
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
                    hx_post="/", hx_target="#chatlist", hx_swap="beforeend",
                    cls="flex space-x-2 mt-2",
                ), cls="p-4 max-w-lg mx-auto")
    return Title('Chatbot Demo'), page

# Handle the form submission
@app.post("/")
def post(msg: str):
    messages.append({"role": "user", "content": msg})

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": msg["role"], "content": msg["content"]} for msg in messages],
    )
    content = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": content})

    return (ChatMessage(messages[-2]), # The user's message
            ChatMessage(messages[-1]), # The chatbot's response
            ChatInput()) # And clear the input field via an OOB swap

if __name__ == '__main__':
    uvicorn.run("basic:app", host='0.0.0.0', port=8000, reload=True)
