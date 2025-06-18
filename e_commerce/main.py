from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, OAuth
from fastlite import database
from faststripe.core import StripeApi

import os, stripe

app, rt = fast_app()

class User: id: int; email: str; oauth_id: str; coins: int = 100
db = database(':memory:')
db.users = db.create(User, transform=True)

class Auth(OAuth):
    def get_auth(self, info, ident, sess, state):
        sess['auth'], sess['email'] = info.sub, info.email
        user = db.users('oauth_id=?', (sess['auth'],))
        if not user: db.users.insert(User(oauth_id=sess['auth'], email=sess['email']))
        return RedirectResponse('/dashboard', status_code=303)

client = GoogleAppClient(os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'))
skip = ('/', '/logout', '/redirect', '/webhook')
oauth = Auth(app, client, skip=skip, login_path='/')

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
sapi = StripeApi(os.environ.get('STRIPE_SECRET_KEY'))
url = 'https://localhost:5001/dashboard'

@rt
def index(req): return Titled('Hello World', A('Login', href=oauth.login_link(req)))

@rt
def dashboard(sess):
    user = db.users('oauth_id=?', (sess['auth'],))[0]
    otp = sapi.one_time_payment('100 Coins', 10_00, url, url, customer_email=user.email)

    return Titled('Dashboard', A('Logout', href='/logout'), P(f'Welcome back {sess["email"]}'), 
                  P(f'You have {user.coins} coins'), A('Buy Coins', href=otp.url, cls='uk-btn'))

@rt
async def webhook(req):
    payload = await req.body()
    try: event = stripe.Webhook.construct_event(payload, req.headers.get('stripe-signature'),
                                                os.environ['STRIPE_WEBHOOK_SECRET'])
    except Exception as e: return Response("Webhook error", status_code=400)

    if event.type == 'checkout.session.completed':
        event_data = event.data.object
        user = db.users('email=?', (event_data.customer_details.email,))[0]
        user.coins += 50
        db.users.update(user)
    return Response(status_code=200)

serve()