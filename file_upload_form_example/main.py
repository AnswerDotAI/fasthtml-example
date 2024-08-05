from fasthtml.common import *
import uvicorn

app = FastHTML(hdrs=(picolink,))

@app.route("/")
def get():
    add = Form(Group(Input(id="myFile", type="file"), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    card = Div(id='todo-list')
    title = 'File Upload Example'
    return Title(title), Main(H1(title), add, card, cls='container')

@app.route("/")
async def post(myFile:UploadFile):
    print(myFile)
    contents = await myFile.read()
    print(contents)
    return "ok"

serve()

