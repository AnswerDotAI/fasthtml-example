from fasthtml.common import *

def ContextMenuItem(label, shortcut, action):
    return Div(
        Span(label),
        Span("|", style="margin: 0 8px; color: #ccc;"),
        Span(shortcut, style="color: #888;"),
        Script(f"""
            me().on('click', ev => {{
                {action}
                me('#context-menu').styles({{display: 'none'}});
            }})
        """),
        style="padding: 8px 12px; cursor: pointer; display: flex; justify-content: space-between; align-items: center;",
    )

def ContextMenu():
    return Div(
        ContextMenuItem("Cut", "Ctrl+X", "console.log('Cut')"),
        ContextMenuItem("Copy", "Ctrl+C", "console.log('Copy')"),
        ContextMenuItem("Paste", "Ctrl+V", "console.log('Paste')"),
        Script("""
            me().on('show', ev => {
                let e = me(ev)
                e.styles({
                    display: 'block',
                    left: ev.detail.x + 'px',
                    top: ev.detail.y + 'px'
                })
            })

            me(document).on('click', ev => {
                if (!me().contains(ev.target)) {
                    me().styles({display: 'none'})
                }
            })

            me(document).on('keydown', ev => {
                const shortcuts = {
                    'x': () => console.log('Cut'),
                    'c': () => console.log('Copy'),
                    'v': () => console.log('Paste')
                }
                if (ev.ctrlKey && shortcuts[ev.key.toLowerCase()]) {
                    ev.preventDefault()
                    shortcuts[ev.key.toLowerCase()]()
                    me().styles({display: 'none'})
                }
            })
        """),
        Style("""
            #my-element {
                padding: 20px;
                background-color: #f0f0f0;
                cursor: context-menu;
            }
        """),
        id="context-menu",
        style="display: none; position: absolute; background: white; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);",
    )