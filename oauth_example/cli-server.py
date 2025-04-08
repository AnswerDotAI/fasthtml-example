from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, redir_url

app,rt = fast_app()
pc_store = {}
cli = GoogleAppClient.from_file('solveit-creds.json')

@rt
def cli_login(request, paircode:str):
    redir = redir_url(request, '/redirect')
    pc_store[paircode] = None
    return cli.login_link(redir, state=paircode)

@rt
def redirect(request, code:str, state:str=None):
    redir = redir_url(request, '/redirect')
    info = cli.retr_info(code, redir)
    if state and state in pc_store:
        pc_store[state] = cli.token["access_token"]
        return 'complete'
    else: return str((state,pc_store))

@rt
def token(paircode:str): return pc_store.pop(paircode, '')

@rt
def index(): return "OAuth CLI Login Server"

serve()
