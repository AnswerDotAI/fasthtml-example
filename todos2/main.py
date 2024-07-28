from fasthtml.common import *

def redir(path='/login'): return RedirectResponse(path, status_code=303)
def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth: return redir()
    todos.xtra(name=auth)

app,rt,(users,User),(todos,Todo) = fast_app(
    'data/data.db',
    before = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/login']),
    hdrs=(SortableJS('.sortable'), MarkdownJS('.markdown')),
    users=dict(name=str, pwd=str, pk='name'),
    todos=dict(id=int, title=str, done=bool, name=str, details=str, priority=int, pk='id')
)

@rt("/login")
def get():
    frm = Form(
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'),
        action='/login', method='post')
    return Titled("Login", frm)

@dataclass
class Login: name:str; pwd:str

@rt("/login")
def post(login:Login, sess):
    if not login.name or not login.pwd: return redir()
    try: u = users[login.name]
    except NotFoundError: u = users.insert(login)
    if not compare_digest(u.pwd.encode("utf-8"), login.pwd.encode("utf-8")): return redir()
    sess['auth'] = u.name
    return redir('/')

@app.get("/logout")
def logout(sess):
    del sess['auth']
    return redir()

@patch
def __ft__(self:Todo):
    show = AX(self.title, f'/todo/{self.id}', 'current-todo')
    edit = AX('edit',     f'/edit/{self.id}', 'current-todo')
    dt = '✅ ' if self.done else ''
    cts = (dt, show, ' | ', edit, Hidden(id="id", value=self.id), Hidden(id="priority", value="0"))
    return Li(*cts, id=f'todo-{self.id}')

new_params = dict(id="new-title", name="title", placeholder="New Todo")
@rt("/")
def get(auth):
    top = Grid(H1(f"{auth}'s Todo list"), Div(A('logout', href='/logout'), style='text-align: right'))
    add = Form(Group(Input(**new_params), Button("Add")), hx_post="/", target_id='todo-list', hx_swap="afterbegin")
    frm = Form(*todos(order_by='priority'), id='todo-list', cls='sortable', hx_post="/reorder", hx_trigger="end")
    card = Card(Ul(frm), header=add, footer=Div(id='current-todo'))
    return Title("Todo list"), Container(top, card)

@rt("/reorder")
def post(id:list[int]):
    for i,id_ in enumerate(id): todos.update({'priority':i}, id_)
    return tuple(todos(order_by='priority'))

@rt("/todo/{id}")
def delete(id:int):
    todos.delete(id)
    return clear('current-todo')

@rt("/edit/{id}")
async def get(id:int):
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), Checkbox(id="done", label='Done'), Textarea(id="details", name="details", rows=10),
        hx_put="/", target_id=f'todo-{id}', id="edit")
    return fill_form(res, todos[id])

@rt("/")
async def put(todo: Todo): return todos.update(todo), clear('current-todo')
@rt("/")
async def post(todo:Todo): return todos.insert(todo), Input(**new_params, hx_swap_oob='true')

@rt("/todo/{id}")
async def get(id:int):
    todo = todos[id]
    btn = Button('delete', hx_delete=f'/todo/{id}', target_id=f'todo-{id}', hx_swap="outerHTML")
    return Div(Div(todo.title), Div(todo.details, cls="markdown"), btn)
serve()
