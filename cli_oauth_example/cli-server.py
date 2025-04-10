from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, redir_url

app,rt = fast_app()
pc_store = {}
cli = GoogleAppClient.from_file('creds.json')
redir_path = '/redirect'

@rt
def cli_login(request, paircode:str):
    pc_store[paircode] = None
    return cli.login_link(redir_url(request, redir_path), state=paircode)

@rt(redir_path)
def redirect(request, code:str, state:str=None):
    redir = redir_url(request, redir_path)
    info = cli.retr_info(code, redir)
    if state and state in pc_store:
        pc_store[state] = cli.token["access_token"]
        return 'complete'
    else: return f"Failed to find {state} in {pc_store}"

@rt
def token(paircode:str):
    if pc_store.get(paircode, ''): return pc_store.pop(paircode)
    return ''

@rt
def index(): return pc_store

serve()
