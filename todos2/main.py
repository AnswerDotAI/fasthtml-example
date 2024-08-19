from fasthtml.common import *
from hmac import compare_digest
# required for sqlalchemy:
from fastsql import *

db = database('data/utodos.db')
# for sqlalchemy:
# url = 'postgresql://'
# db = Database(url)
class User: name:str; pwd:str
class Todo: id:int; title:str; done:bool; name:str; details:str; priority:int
users = db.create(User, pk='name')
todos = db.create(Todo)

login_redir = RedirectResponse('/login', status_code=303)

def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth: return login_redir
    todos.xtra(name=auth)

def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))

bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/login'])
app,rt = fast_app(before=bware,
                  exception_handlers={404: _not_found},
                  hdrs=(SortableJS('.sortable'), MarkdownJS('.markdown')))

@app.get
def login():
    frm = Form(action='/login', method='post')(
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'))
    return Titled("Login", frm)

@dataclass
class Login: name:str; pwd:str

@rt("/login")
def post(login:Login, sess):
    if not login.name or not login.pwd: return login_redir
    try: u = users[login.name]
    except NotFoundError: u = users.insert(login)
    if not compare_digest(u.pwd.encode("utf-8"), login.pwd.encode("utf-8")): return login_redir
    sess['auth'] = u.name
    return RedirectResponse('/', status_code=303)

@app.get("/logout")
def logout(sess):
    del sess['auth']
    return login_redir

@patch
def __ft__(self:Todo):
    ashow = A(self.title, hx_post=retr.rt(id=self.id), target_id='current-todo')
    aedit = A('edit',     hx_post=edit.rt(id=self.id), target_id='current-todo')
    dt = '✅ ' if self.done else ''
    cts = (dt, ashow, ' | ', aedit, Hidden(id="id", value=self.id), Hidden(id="priority", value="0"))
    return Li(*cts, id=f'todo-{self.id}')

@rt("/")
def get(auth):
    title = f"{auth}'s Todo list"
    top = Grid(H1(title),
               Div(A('logout', href='/logout'),
                   style='text-align: right'))
    new_inp = Input(id="new-title", name="title", placeholder="New Todo")
    add = Form(hx_post=create, target_id='todo-list', hx_swap="afterbegin")(
               Group(new_inp, Button("Add")))
    frm = Form(id='todo-list', cls='sortable', hx_post=reorder, hx_trigger="end")(
               *todos(order_by='priority'))
    card = Card(Ul(frm), header=add, footer=Div(id='current-todo'))
    return Title(title), Container(top, card)

@rt
def reorder(id:list[int]):
    for i,id_ in enumerate(id): todos.update(priority=i, id=id_)
    return tuple(todos(order_by='priority'))

@rt
def create(todo:Todo):
    new_inp = Input(id="new-title", name="title", placeholder="New Todo", hx_swap_oob='true')
    return todos.insert(todo), new_inp

@rt
def remove(id:int):
    todos.delete(id)
    return clear('current-todo')

@rt
def edit(id:int):
    res = Form(hx_post=replace, target_id=f'todo-{id}', id="edit")(
            Group(Input(id="title"), Button("Save")),
            Hidden(id="id"), Hidden(priority="priority"),
            Hidden(name="done"), CheckboxX(id="done", label='Done'),
            Textarea(id="details", name="details", rows=10))
    return fill_form(res, todos[id])

@rt
def replace(todo: Todo): return todos.update(todo), clear('current-todo')

@rt
def retr(id:int):
    todo = todos[id]
    btn = Button('delete',
                 name='id', value=id, target_id=f'todo-{todo.id}',
                 hx_post=remove, hx_swap="outerHTML")
    return Div(H2(todo.title), Div(todo.details, cls="markdown"), btn)

serve()

