from fasthtml.common import *
from monsterui.all import *

import asyncio, os, pty, select

# Global variables for PTY management
fd = None
streaming_task = None

def spawn_shell():
    pid, fd = pty.fork()
    if pid == 0: os.execvp(os.environ.get("SHELL", "/bin/bash"), ["bash"])
    return fd

def read_pty(fd): 
    'Read from PTY and print output'
    try:
        r,*_ = select.select([fd], [], [], 0.01)  # Shorter timeout for better responsiveness
        if r: return os.read(fd, 1024).decode()
    except OSError as e: print(e)

async def stream_output(send):
    """Continuously read from PTY and send to WebSocket"""
    while True:
        try:
            output = read_pty(fd)
            if output:
                await send(output)
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
        except Exception as e:
            print(f"Streaming error: {e}")
            break

hdrs = (Script(src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js", type="module"),    # xterm glue code
        Script(src="/static/terminal.js", type="module"),    # xterm glue code
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.min.css"),
        Theme.blue.headers())

app, rt = fast_app(hdrs=hdrs,routes=(Mount('/static', StaticFiles(directory=f'./static')),))

async def on_conn(send):
    global fd, streaming_task
    fd = spawn_shell()
    # Start continuous streaming task
    streaming_task = asyncio.create_task(stream_output(send))
    
async def on_disconn(*args): 
    global streaming_task
    if streaming_task:
        streaming_task.cancel()
    if fd:
        os.close(fd)

@app.ws('/ws', conn=on_conn, disconn=on_disconn)
async def on_message(msg: str, send):
    'Write incoming message to existing PTY - streaming handles output'
    if fd:
        os.write(fd, msg.encode())

@rt
def index():
    card = Card(Div(id='terminal', cls="w-full h-[600px] bg-black text-white"),
                header=H4("Web Terminal"), cls="mt-6")
    return Title("Terminal Demo"), *hdrs, card

serve()