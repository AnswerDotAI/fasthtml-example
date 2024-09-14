"""Example from https://github.com/fabge/fasthtml-sse/"""
from fasthtml.common import *
from claudette import *
import asyncio
from starlette.responses import StreamingResponse

# Set up the app, including daisyui and tailwind and the htmx sse extension for the chat component
tlink = (Script(src="https://cdn.tailwindcss.com"),)
dlink = Link(
    rel="stylesheet",
    href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
)
sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
app = FastHTML(hdrs=(tlink, dlink, picolink, sselink), live=True)

# Set up a chat model client and list of messages (https://claudette.answer.ai/)
cli = Client(models[-1])
sp = """You are a helpful and concise assistant."""
messages = []


# @app.get("/{fname:path}.{ext:static}")
# def static(fname: str, ext: str):
#     return FileResponse(f"{fname}.{ext}")

# Send messages to the chat model and yield the responses
async def message_generator():
    print("message_generator", messages)
    r = cli(messages[:-1], sp=sp, stream=True)
    for chunk in r:
        messages[-1]["content"] += chunk
        yield f"event: message\ndata: {chunk}\n\n"
        await asyncio.sleep(0.5)
    yield f"event: close\ndata: \n\n"


# Chat message component (renders a chat bubble)
# Now with a unique ID for the content and the message
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = (
        "chat-bubble-primary" if msg["role"] == "user" else "chat-bubble-secondary"
    )
    chat_class = "chat-end" if msg["role"] == "user" else "chat-start"
    return Div(
        Div(msg["role"], cls="chat-header"),
        Div(
            msg["content"],
            id=f"chat-content-{msg_idx}",  # Target if updating the content
            cls=f"chat-bubble {bubble_class}",
            **kwargs,
        ),
        id=f"chat-message-{msg_idx}",  # Target if replacing the whole message
        cls=f"chat {chat_class}",
    )


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(
        type="text",
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="true",
    )


# The main screen
@app.route("/")
def get():
    page = Body(
        H1("Chatbot SSE (server-sent events) Demo"),
        Div(
            *[ChatMessage(msg) for msg in messages],
            id="chatlist",
            cls="chat-box h-[73vh] overflow-y-auto",
        ),
        Form(
            Group(ChatInput(), Button("Send", cls="btn btn-primary")),
            hx_post="/send-message",
            hx_target="#chatlist",
            hx_swap="beforeend",
            cls="flex space-x-2 mt-2",
        ),
        cls="p-4 max-w-lg mx-auto",
    )
    return Title("Chatbot Demo"), page


@app.get("/get-message")
async def get_message():
    return StreamingResponse(message_generator(), media_type="text/event-stream")


@app.post("/send-message")
def send_message(msg: str):
    messages.append({"role": "user", "content": msg})
    user_msg = Div(ChatMessage(len(messages) - 1))
    messages.append({"role": "assistant", "content": ""})
    # The returned assistant message uses the SSE extension, connect to the /get-message endpoint and get all messages until the close event
    assistant_msg = Div(
        ChatMessage(
            len(messages) - 1,
            hx_ext="sse",
            sse_connect="/get-message",
            sse_swap="message",
            sse_close="close",
            hx_swap="beforeend",
        )
    )
    return user_msg, assistant_msg, ChatInput()


serve()
