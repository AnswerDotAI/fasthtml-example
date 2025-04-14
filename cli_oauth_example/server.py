from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, redir_url
from fastlite import *

db = database('data.db')
class User: auth:str
users = db.create(User, pk='auth')

app,rt = fast_app()
pc_store = {}
cli = GoogleAppClient.from_file('creds.json')
redir_path = '/redirect'

@rt
async def cli_login(request, paircode:str):
    pc_store[paircode] = None
    return cli.login_link(redir_url(request, redir_path), state=paircode)

@rt(redir_path)
async def redirect(request, code:str, state:str=None):
    redir = redir_url(request, redir_path)
    auth = cli.retr_id(code, redir)
    if state and state in pc_store:
        pc_store[state] = auth
        if auth not in users: users.insert(User(auth=auth))
        return 'complete'
    else: return f"Failed to find {state} in {pc_store}"

@rt
async def token(paircode:str, sess):
    if pc_store.get(paircode, ''):
        auth = pc_store.pop(paircode)
        sess['auth'] = auth
        return auth

@rt
async def secured(sess):
    return sess['auth']

@rt
def index(): return pc_store

serve()

