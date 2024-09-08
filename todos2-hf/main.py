from fasthtml.common import *
from fasthtml_hf import setup_hf_backup

def tid(id): return f'todo-{id}'
def lookup_user(u,p):
    try: user = users[u]
    except NotFoundError: user = users.insert(name=u, pwd=p)
    return user.pwd==p

authmw = user_pwd_auth(lookup_user, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css'])
def before(auth): todos.xtra(name=auth)

app,rt,(users,User),(todos,Todo) = fast_app(
    'data/utodos.db', middleware=authmw, before=before,
    users=dict(name=str, pwd=str, pk='name'),
    todos=dict(id=int, title=str, done=bool, name=str, details=str, priority=int, pk='id'))

@patch
def __ft__(self:Todo):
    show = AX(self.title, f'/todos/{self.id}', 'current-todo')
    edit = AX('edit',     f'/edit/{self.id}' , 'current-todo')
    dt = ' (done)' if self.done else ''
    return Li(show, dt, ' | ', edit, id=tid(self.id))

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)
def clr_details(): return Div(hx_swap_oob='innerHTML', id='current-todo')

@rt("/")
def get(request, auth):
    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    card = Card(Ul(*todos(), id='todo-list'),
                header=add, footer=Div(id='current-todo')),
    title = 'Todo list'
    top = Grid(H1(f"{auth}'s {title}"), Div(A('logout', href=basic_logout(request), target="_blank"), style='text-align: right'))
    return Title(title), Main(top, card, cls='container')

@rt("/todos/{id}")
def delete(id:int):
    todos.delete(id)
    return clr_details()

@rt("/")
def post(todo:Todo): return todos.insert(todo), mk_input(hx_swap_oob='true')

@rt("/edit/{id}")
def get(id:int):
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), CheckboxX(id="done", label='Done'),
        hx_put="/", target_id=tid(id), id="edit")
    return fill_form(res, todos[id])

@rt("/")
def put(todo: Todo): return todos.upsert(todo), clr_details()

@rt("/todos/{id}")
def get(id:int):
    todo = todos[id]
    btn = Button('delete', hx_delete=f'/todos/{todo.id}',
                 target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title), btn)

setup_hf_backup(app)
serve()
