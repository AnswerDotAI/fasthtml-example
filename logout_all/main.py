from dataclasses import dataclass
from datetime import datetime, UTC
from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, OAuth

import os

def now(): return int(datetime.now(UTC).timestamp()) 

@dataclass
class User: id: str; logout_time: int
db = database('/tmp/data.db')
db.users = db.create(User, transform=True)

logout_time = now()

class Auth(OAuth):
    def get_auth(self, info, ident, session, state):
        if not info.sub: RedirectResponse('/login', status_code=303)
        db.users.upsert(User(id=info.sub, logout_time=now()))
        session['login_time'] = now()
        return RedirectResponse('/', status_code=303)
    
    def check_invalid(self, req, session, auth):
        if session.get('login_time', 0) < db.users[auth].logout_time:
            session.pop('auth', None)
            return RedirectResponse('/login', status_code=419)
        return False

app,rt = fast_app()
cli = GoogleAppClient(os.environ['GOOGLE_CLIENT_ID'], os.environ['GOOGLE_CLIENT_SECRET'])
oauth = Auth(app, cli)

@rt
def logout(session):
    if auth := session.pop('auth', None): db.users.upsert(id=auth, logout_time=now())
    return oauth.redir_login(session)

@rt
def home(auth): return P('Logged in!'), A('Log out', href='/logout')

@app.get('/login')
def login(req): return Div(P("Not logged in"), A('Log in', href=oauth.login_link(req)))

serve()