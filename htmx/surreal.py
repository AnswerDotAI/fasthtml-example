from fasthtml.common import *
app,rt = fast_app()

@rt("/")
def get():
    return Titled('Hello',
        H2("fadeOut() Demo"),
        Safe('I fade <i>out</i> and <i>remove</i> my italics.'),
        Any('i', 'await sleep(1000); e.fadeOut()'),
        Button('Click me to remove me.', On('e.fadeOut()')),
        H2("On() Demo"),
        Div("I change color when clicked.",
            On("e.styles('background-color: lightblue');")
        ),        
        H2("AnyOn() Demo"),
        Button("Button 1"),
        Button("Button 2"),
        Button("Button 3"),
        AnyOn("button", "e.classToggle('highlight');"),
        H2("Prev() Demo"),
        Input(type="text", placeholder="Type here"),
        Prev("e.value = e.value.toUpperCase();", event="input"),
        Style(".highlight { background-color: yellow; }")
    )

serve()
