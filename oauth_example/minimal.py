from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient
import json

# Auth client
client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"), 
                         os.getenv("AUTH_CLIENT_SECRET"),
                         redirect_uri="http://localhost:8000/auth_redirect")

app = FastHTML()

@app.get('/')
def home():
    return P("Login link: ", A("click here", href=client.login_link()))

@app.get('/auth_redirect')
def auth_redirect(code:str, session):
    info = client.retr_info(code)
    return H1("Profile info"), P(json.dumps(info))

serve(port=8000)