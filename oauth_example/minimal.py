from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient
import json

# Auth client
client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"),
                         os.getenv("AUTH_CLIENT_SECRET"))
redirect_uri = "http://localhost:5001/redirect"

app = FastHTML()

@app.get('/')
def home():
    link = client.login_link(redirect_uri)
    return P("Login link: ", A("click here", href=link))

@app.get('/redirect')
def auth_redirect(request, code:str):
    info = client.retr_info(code, redirect_uri)
    return H1("Profile info"), P(json.dumps(info))

serve()

