from fasthtml.all import *
import uvicorn


style = Link(rel="stylesheet", href="doodle.css")
font = Style("""@import url('https://fonts.googleapis.com/css2?family=Short+Stack&display=swap');""")
body_style = "max-width: 700px; background-color: lavender; font-family: 'Short Stack', cursive;"
app = FastHTML(hdrs=(style, font))


# Main page
@app.get("/")
def home():
    inp = Input(id="new-prompt", name="prompt", placeholder="Enter a prompt")
    add = Form(Group(inp, Button("Generate")), hx_post="/", target_id='gen-list', hx_swap="afterbegin")
    gen_list = Div(id='gen-list')
    f = Fieldset(
        Legend("Extra Inputs"),
        P(Label("Negative Prompt", for_="example-input-text"), Br(), Input(id="example-input-text", type_="text", placeholder="Enter some text here")),
        P(Label("Extra long description", for_="example-textarea"), Br(),Textarea(id="example-textarea", rows="3")),
        P(Label("Add upscaling?", for_="ch1"), Br(), Checkbox("No", id="ch1")),
        P(Label("Enable Warp Drive?", for_="ch2"), Br(),Checkbox(id="ch2")),
    )
    return Title('Image Generation Demo'), Body(H1('Magic Image Generation'), add, gen_list, f, 
                                                cls='doodle', style=body_style)

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')


if __name__ == '__main__':
  uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)