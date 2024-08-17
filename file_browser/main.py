from pathlib import Path

from fasthtml.common import *


FILE = "📄"
FOLDER = "📁"
SPACE = "\u2800"

app, rt = fast_app()

@rt("/{path:path}")
def get(path: str):
    p1 = Path(path)
    content1 = {p2.name: p2.is_dir() for p2 in p1.iterdir()}
    directories = [name for name, is_dir in content1.items() if is_dir]
    files = [name for name, is_dir in content1.items() if not is_dir]
    directories.sort()
    files.sort()
    content2 = []
    if p1.parts:
        content2.append(P(SPACE * (len(p1.parts) - 1) + "⌄" + FOLDER + p1.name))
    spaces = SPACE * len(p1.parts)
    for name in directories:
        content2.append(P(spaces + ">" + FOLDER + name, hx_get=f"{path}/{name}", hx_swap="outerHTML"))
    for name in files:
        content2.append(P(spaces + SPACE + FILE + name))
    return Div(*content2)

serve()
