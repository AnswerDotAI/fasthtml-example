from fasthtml.common import *

import asyncio, fcntl, os, pty, select, signal, struct, termios

class MiniTerm:
    def __init__(self): self.fd,self.pid = None,None

    def read_pty(self): 
        "Read from PTY and print output"
        try:
            r,*_ = select.select([self.fd], [], [], 0.01)
            if r: return os.read(self.fd, 1024).decode()
        except OSError as e: print(e)

    async def stream(self, send):
        'Continuously read from PTY and send to WebSocket'
        while True:
            if (o := self.read_pty()): await send(o)
            await asyncio.sleep(0.01)

    def spawn(self, send):
        "Fork process and replace child with solveit login shell"
        if self.fd: return
        self.pid,self.fd = pty.fork()
        if self.pid == 0: os.execvp("bash", ["bash", "-l"])
        self.task = asyncio.create_task(self.stream(send))

    def stop(self):
        if self.fd: self.task.cancel()
        try: os.killpg(os.getpgid(self.pid), signal.SIGTERM)
        except (OSError,ProcessLookupError): pass  # Process may have already terminated
        os.close(self.fd)
        self.fd = None

    def write(self, msg:str):
        'Write incoming message to existing PTY - stream handles output'
        if self.fd: os.write(self.fd, msg.encode())

hdrs = (Script(src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js", type="module"),
        Script(src="/static/terminal.js", type="module"),
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.min.css"))

app, rt = fast_app(hdrs=hdrs,routes=(Mount('/static', StaticFiles(directory=f'./static')),))

async def on_conn(send):  term.spawn(send)
async def on_disconn(*_): term.stop()

@app.ws('/ws', conn=on_conn, disconn=on_disconn)
async def on_message(msg:str='', cols:int=0, rows:int=0):
    'Write incoming message to existing PTY, then read from it.'
    if msg: term.write(msg)
    elif cols and term.fd:
        fcntl.ioctl(term.fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))

@rt
def index():
    global term
    term = MiniTerm()
    card = Card(Div(id='terminal', cls="w-full h-[600px] bg-black text-white"),
                header=H4("Web Terminal"), cls="mt-6")
    return Title("Terminal Demo"), *hdrs, card

serve()