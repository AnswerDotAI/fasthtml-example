from components.code_editor import CodeEditor
from components.context_menu import ContextMenu
from dotenv import load_dotenv
from fasthtml.common import *
from fireworks.client import Fireworks
import os

load_dotenv()

client = Fireworks(api_key=os.getenv("FIREWORKS_API_KEY"))
model_name = "accounts/fireworks/models/starcoder-16b"

# Tailwind CSS
tailwind_css = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")

# Ace Editor
ace_editor = Script(src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js")

# Tippy JS
tippy_css = Link(rel="stylesheet", href="https://unpkg.com/tippy.js@6/dist/tippy.css")
tippy_js = Script(src="https://unpkg.com/@popperjs/core@2")
tippy_js2 = Script(src="https://unpkg.com/tippy.js@6")

global_style = Style("""
body, html {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}
#editor {
    position: absolute;
    top: 64px;  /* Height of the toolbar */
    right: 0;
    bottom: 0;
    left: 0;
}
""")

app = FastHTML(hdrs=(tailwind_css, ace_editor, global_style, tippy_css, tippy_js, tippy_js2))
rt = app.route

@rt("/")
def get():
    return Title("Code Editor"), CodeEditor(), ContextMenu()

@rt("/complete")
async def post(request: Request):
    data = await request.json()
    code = data['code']
    row = data['row']
    column = data['column']
    
    try:
        response = client.completion.create(
            model=model_name,
            prompt=code,
            max_tokens=64,
            stop=["\n"]  # Stop generation at new line
        )
        completion = response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating completion: {e}")
        completion = "Error generating completion"

    return JSONResponse({"completion": completion})

serve()