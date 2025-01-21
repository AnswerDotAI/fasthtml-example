# Websocket steaming chat with Llamaindex Open AI Agent
## Requirements:
## llama-index-agent-openai

from fasthtml.common import *
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
import os

# check if api key is in the environment variables
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("OPENAI_API_KEY not found in the environment variables")


# Set up the app, including daisyui and tailwind for the chat component
headers = (
    Script(src="https://cdn.tailwindcss.com"),  
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"),
)

# Set up the app, including daisyui and tailwind for the chat component
app = FastHTML(hdrs=headers, exts='ws', pico = False, debug=True)


# Initialize Llamaindex RAG OpenAI agent 
llm = OpenAI(model="gpt-4o")
openai_agent = OpenAIAgent.from_tools(llm=llm)

messages=[]

# Chat message component (renders a chat bubble)
# Now with a unique ID for the content and the message
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = "chat-bubble-primary" if msg['role']=='user' else 'chat-bubble-secondary'
    chat_class = "chat-end" if msg['role']=='user' else 'chat-start'
    return Div(Div(msg['role'], cls="chat-header"),
               
                    Div(msg['content'], # TODO: support markdown                   
                    id=f"chat-content-{msg_idx}", # Target if updating the content
                    cls=f"chat-bubble {bubble_class}"
                   ),
                    
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
    page = Body(
                # Chat messages
                Div(*[ChatMessage(msg_idx) for msg_idx, msg in enumerate(messages)],
                    id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                
                # Input field and send button
                Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
                    ws_send=True, hx_ext="ws", ws_connect="/wscon",
                    cls="flex space-x-2 mt-2"),
                
                cls="p-4 max-w-lg mx-auto")
    
    return Titled("Chatbot Demo", page )


@app.ws('/wscon')
async def ws(msg:str, send):
    
    # add user message to messages list
    messages.append({"role":"user", "content":msg.rstrip()})
    swap = 'beforeend'
    

    # Send the user message to the user (updates the UI right away)
    await send(Div(ChatMessage(len(messages)-1), hx_swap_oob=swap, id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())   
    
    # Send an empty message with the assistant response
    messages.append({"role":"assistant", "content":""})
    await send(Div(ChatMessage(len(messages)-1), hx_swap_oob=swap, id="chatlist"))
   
    # Start OpenAI agent async streaming chat
    response_stream = await openai_agent.astream_chat(msg) 

    # Get and process async streaming chat response chunks
    async for chunk_message in response_stream.async_response_gen():
        print(chunk_message, end='', flush=True) # Check streaming response via print
        messages[-1]["content"] += chunk_message 
        await send(Span(chunk_message, hx_swap_oob=swap, id=f"chat-content-{len(messages)-1}"))


if __name__ == '__main__':
    serve()