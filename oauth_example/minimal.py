from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient
import json

# Auth client
redirect_uri = "http://localhost:8000/auth_redirect"
client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"), 
                         os.getenv("AUTH_CLIENT_SECRET"),
                         redirect_uri=redirect_uri)

app = FastHTML()

@app.get('/')
def home():
    return P("Login link: ", A("click here", href=client.login_link(redirect_uri=redirect_uri)))

@app.get('/auth_redirect')
def auth_redirect(code:str, session):
    info = client.retr_info(code, redirect_uri=redirect_uri)
    return H1("Profile info"), P(json.dumps(info))

serve(port=8000)