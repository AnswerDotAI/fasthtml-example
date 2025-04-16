from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient
import json

client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"), os.getenv("AUTH_CLIENT_SECRET"))
redirect_uri = "http://localhost:5001/redirect"
app,rt = fast_app()

@rt
def index():
    return P("Login link: ", A("click here", href=client.login_link(redirect_uri)))

@rt
def redirect(request, code:str):
    info = client.retr_info(code, redirect_uri)
    return H1("Profile info"), P(json.dumps(info))

serve()

