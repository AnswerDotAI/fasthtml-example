from fasthtml.all import *
from fastcore.utils import *
from fasthtml.components import Script
import uvicorn

# The original, no syntax highlighting
def MarkdownJS(sel='.marked'):
    src = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
htmx.onLoad(elt => htmx.findAll(elt, "%s").forEach(e => e.innerHTML = marked.parse(e.textContent)));
""" % sel
    return Script(NotStr(src), type='module')

# New version with copy button and syntax highlighting
def HighlightMarkdownJS(sel='.marked', lang='python'):
    src = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
hljs.addPlugin(new CopyButtonPlugin());
htmx.onLoad(elt => {
htmx.findAll(elt, "%s").forEach(e => e.innerHTML = marked.parse(e.textContent));
hljs.highlightAll();
});""" % sel
    # First two links are highlight.js styles, can also use default.css + dark.css or any of https://github.com/highlightjs/highlight.js/tree/main/src/styles
    return [Link(rel='stylesheet', media="(prefers-color-scheme: light)", href='https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.css'),
            Link(rel='stylesheet', media="(prefers-color-scheme: dark)", href='https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.css'),
            Script(src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"),
            Script(src=f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/{lang}.min.js"),
            Script(src="https://unpkg.com/highlightjs-copy/dist/highlightjs-copy.min.js"),
            Link(rel='stylesheet', href='https://unpkg.com/highlightjs-copy/dist/highlightjs-copy.min.css'),
            Script(NotStr(src), type='module')]

app = FastHTML(hdrs=(picolink, *HighlightMarkdownJS()))

@app.route("/")
def get():
    title = 'Code Snippet Example'
    code_text = '\n'.join(open(__file__, 'r').read().split("\n")[31:42])
    markdown = Div("### Usage:\n```python\n" + code_text + "\n```", cls='marked')
    return Title(title), Main(H1(title), markdown, cls='container')

if __name__ == '__main__':
  uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)