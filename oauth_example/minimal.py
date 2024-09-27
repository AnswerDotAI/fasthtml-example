from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient, redir_url
import json

# Auth client
client = GitHubAppClient(os.getenv("GHAUTH_CLIENT_ID"),
                         os.getenv("GHAUTH_CLIENT_SECRET"))

app = FastHTML()
redir_path = '/auth_redirect'

@app.get('/')
def home(request):
    redir = redir_url(request, redir_path)
    link = client.login_link(redir)
    return P("Login link: ", A("click here", href=link))

@app.get(redir_path)
def auth_redirect(request, code:str):
    redir = redir_url(request, redir_path)
    info = client.retr_info(code, redir)
    return H1("Profile info"), P(json.dumps(info))

serve(port=8000)

