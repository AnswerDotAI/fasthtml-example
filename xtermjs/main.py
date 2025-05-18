from fasthtml.common import *
from monsterui.all import *
from threading import Thread

import asyncio, os, pty, select

def spawn_shell():
    pid, fd = pty.fork()
    if pid == 0: os.execvp(os.environ.get("SHELL", "/bin/bash"), ["bash"])
    return fd

def read_pty(fd): 
    'Read from PTY and print output'
    try:
        r,_,_ = select.select([fd], [], [], 0.1)
        if r: return os.read(fd, 1024).decode()
    except OSError as e: print(e)

hdrs = (Script(src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js", type="module"),    # xterm glue code
        Script(src="/static/terminal.js", type="module"),    # xterm glue code
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.min.css"),
        Theme.blue.headers())

app, rt = fast_app(hdrs=hdrs,routes=(Mount('/static', StaticFiles(directory=f'./static')),))

async def on_conn(send):
    global fd
    fd = spawn_shell()
    await send(read_pty(fd))
async def on_disconn(*args): os.close(fd)

@app.ws('/ws', conn=on_conn, disconn=on_disconn)
async def on_message(msg: str, send):
    'Write incoming message to existing PTY, then read from it.'
    os.write(fd, msg.encode())
    await asyncio.sleep(.1)
    await send(read_pty(fd))

@rt
def index():
    card = Card(Div(id='terminal', cls="w-full h-[600px] bg-black text-white"),
                header=H4("Web Terminal"), cls="mt-6")
    return Title("Terminal Demo"), *hdrs, card

serve()