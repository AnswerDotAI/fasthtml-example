from fasthtml.common import *
from fasthtml.oauth import GitHubAppClient, OAuth

client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"),
                         os.getenv("AUTH_CLIENT_SECRET"))

class Auth(OAuth):
    def get_auth(self, info, ident, session, state):
        if info.login=='johnowhitaker':
            return RedirectResponse('/', status_code=303)

app = FastHTML()
oauth = Auth(app, client)

@app.get('/')
def home(auth): return P('Logged in!'), A('Log out', href='/logout')

@app.get('/login')
def login(req): return Div(P("Not logged in"), A('Log in', href=oauth.login_link(req)))

serve()

