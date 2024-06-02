from fasthtml.all import *
import uvicorn

path = Path('data')
path.mkdir(exist_ok=True)
db = Database(path/'todos.db')
db.enable_wal()
todos = db.t.todos
if todos not in db.t: todos.create(id=int, title=str, done=bool, pk='id')
Todo = todos.dataclass()

id_curr = 'current-todo'
def tid(id): return f'todo-{id}'

@patch
def __xt__(self:Todo):
    show = AX(self.title, f'/todos/{self.id}', id_curr)
    edit = AX('edit',     f'/edit/{self.id}' , id_curr)
    dt = ' (done)' if self.done else ''
    return Li(show, dt, ' | ', edit, id=tid(self.id))

css = Style(':root { --pico-font-size: 100%; }')
app = FastHTML(hdrs=(picolink, css))
rt = app.route

@rt("/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)
def clr_details(): return Div(hx_swap_oob='innerHTML', id=id_curr)

@rt("/")
async def get():
    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    card = Card(Ul(*todos(), id='todo-list'),
                header=add, footer=Div(id=id_curr)),
    title = 'Todo list'
    return Title(title), Main(H1(title), card, cls='container')

@rt("/todos/{id}")
async def delete(id:int):
    todos.delete(id)
    return clr_details()

@rt("/")
async def post(todo:Todo): return todos.insert(todo), mk_input(hx_swap_oob='true')

@rt("/edit/{id}")
async def get(id:int):
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), Checkbox(id="done", label='Done'),
        hx_put="/", target_id=tid(id), id="edit")
    return fill_form(res, todos.get(id))

@rt("/")
async def put(todo: Todo): return todos.upsert(todo), clr_details()

@rt("/todos/{id}")
async def get(id:int):
    todo = todos.get(id)
    btn = Button('delete', hx_delete=f'/todos/{todo.id}',
                 target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title), btn)

if __name__ == '__main__': uvicorn.run("main:app", port=os.getenv("PORT", default=5000))

