from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, OAuth

cli = GoogleAppClient.from_file('/Users/jhoward/git/_nbs/oauth-test/client_secret.json')

class Auth(OAuth):
    def login(self, info, state): return RedirectResponse('/', status_code=303)
    def chk_auth(self, info, ident, session):
        email = info.email or ''
        return info.email_verified and email.split('@')[-1]=='answer.ai'

app = FastHTML()
oauth = Auth(app, cli)

@app.get('/')
def home(auth): return P('Logged in!'), A('Log out', href='/logout')

@app.get('/login')
def login(req): return Div(P("Not logged in"), A('Log in', href=oauth.login_link(req)))

serve()

