from fasthtml.common import *
app,rt = fast_app()

@rt("/")
def get():
    return Titled('Surreal.js demo',
        H3("fadeOut()"),
        Safe('I fade <i>out</i> and <i>remove</i> my italics.'),
        AnyNow('i', 'await sleep(1000); e.fadeOut()'),
        Button('Click me to remove me.', On('e.fadeOut()')),

        H3("On()"),
        Div("I change color when clicked.",
            On("e.styles('background-color: lightblue');")),

        H3("Any()"),
        Style(".highlight { background-color: yellow; }"),
        Button("Button 1"), Button("Button 2"), Button("Button 3"),
        Any("button", "e.classToggle('highlight');"),

        H3("Prev()"),
        Input(type="text", placeholder="Type here"),
        Prev("e.value = e.value.toUpperCase();", event="input"),
    )

serve()
