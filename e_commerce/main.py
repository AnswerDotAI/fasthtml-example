from fastcore.basics import patch
from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, OAuth
from fastlite import database
from faststripe.core import StripeApi

import os, stripe

app, rt = fast_app()

class User: id: int; email: str; oauth_id: str; credits: int = 100
class Transaction: id: int; uid: int; amount: int

db = database('e_comm.db')
db.users = db.create(User, transform=True)
# Use a transaction payment model for easier auditing
db.transactions = db.create(Transaction, transform=True, foreign_keys=[('uid', 'user')])

@patch
def mk_txn(self: Database, uid, amt): return self.transactions.insert(Transaction(uid=uid, amount=amt))

@patch
def credits(self: Database, uid): return sum(t.amount for t in self.transactions('uid=?', [uid]))

class Auth(OAuth):
    def get_auth(self, info, ident, sess, state):
        'Custom OAuth class handles Google authentication and automatic user creation'
        sess['auth'] = info.sub
        user = db.users('oauth_id=?', (sess['auth'],))
        if not user:
            user = db.users.insert(User(oauth_id=sess['auth'], email=info.email))
            db.mk_txn(user.id, 100)
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
    'Simple dashboard with a otp link for purchasing more credits'
    user = db.users('oauth_id=?', (sess['auth'],))[0]
    otp = sapi.one_time_payment('100 Credits', 10_00, url, url, customer_email=user.email)

    return Titled('Dashboard', A('Logout', href='/logout'), P(f'Welcome back {user.email}'), 
                  P(f'You have {db.credits(user.id)} credits'), A('Buy Credits', href=otp.url, cls='uk-btn'))

@rt
async def webhook(req):
    'Handles Stripe webhooks to update user credits after successful payment'
    payload = await req.body()

    # need to verify the request came from stripe
    try: event = stripe.Webhook.construct_event(payload, req.headers.get('stripe-signature'),
                                                os.environ['STRIPE_WEBHOOK_SECRET'])
    except Exception as e: return Response("Webhook error", status_code=400)

    if event.type == 'checkout.session.completed':
        event_data = event.data.object
        user = db.users('email=?', (event_data.customer_details.email,))[0]
        db.mk_txn(user.id, 100)
    return Response(status_code=200)

serve()