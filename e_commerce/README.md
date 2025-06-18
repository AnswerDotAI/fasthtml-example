# Complete App Example

A full-featured FastHTML application demonstrating OAuth authentication, database integration, and Stripe payment processing with a coin-based system.

## Features

- Google OAuth authentication
- User registration and management
- Coin-based virtual currency system
- Stripe payment integration for purchasing coins
- Webhook handling for payment confirmation
- Session management and protected routes

## Technology Stack

- [FastHTML](https://github.com/AnswerDotAI/fasthtml): A Python framework for building dynamic web applications
- [FastLite](https://github.com/AnswerDotAI/fastlite): Database integration
- [FastStripe](https://github.com/AnswerDotAI/faststripe): Stripe payment processing
- Google OAuth: User authentication
- SQLite: User data storage

## Implementation Highlights

### App Setup and Database

The app uses FastHTML's `fast_app` function and creates an in-memory SQLite database with a User model:

```python
app, rt = fast_app()

class User: id: int; email: str; oauth_id: str; coins: int = 100
db = database(':memory:')
db.users = db.create(User, transform=True)
```

### OAuth Authentication

Custom OAuth class handles Google authentication and automatic user creation:

```python
class Auth(OAuth):
    def get_auth(self, info, ident, sess, state):
        sess['auth'], sess['email'] = info.sub, info.email
        user = db.users('oauth_id=?', (sess['auth'],))
        if not user: db.users.insert(User(oauth_id=sess['auth'], email=sess['email']))
        return RedirectResponse('/dashboard', status_code=303)

client = GoogleAppClient(os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET'))
oauth = Auth(app, client, skip=skip, login_path='/')
```

### Stripe Integration

Uses FastStripe to create one-time payments for coin purchases:

```python
@rt
def dashboard(sess):
    user = db.users('oauth_id=?', (sess['auth'],))[0]
    otp = sapi.one_time_payment('100 Coins', 10_00, url, url, customer_email=user.email)
    
    return Titled('Dashboard', A('Logout', href='/logout'), P(f'Welcome back {sess["email"]}'), 
                  P(f'You have {user.coins} coins'), A('Buy Coins', href=otp.url, cls='uk-btn'))
```

### Webhook Processing

Handles Stripe webhooks to update user coins after successful payment:

```python
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
```

## Setup

### 1. Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the OAuth consent screen if prompted
6. Set Application type to "Web application"
7. Add `http://localhost:5001/redirect` to "Authorized redirect URIs"
8. Copy the Client ID and Client Secret

### 2. Stripe Setup

1. Create a [Stripe account](https://stripe.com/)
2. Go to the Stripe Dashboard
3. Get your "Secret key" from the API keys section (use test keys for development)
4. Install the [Stripe CLI](https://stripe.com/docs/stripe-cli)
5. Login to Stripe CLI: `stripe login`
6. Get your webhook signing secret: `stripe listen --forward-to localhost:5001/webhook`
7. Copy the webhook signing secret from the CLI output

### 3. Environment Variables

Set the following environment variables:

```bash
export GOOGLE_CLIENT_ID=your_google_client_id
export GOOGLE_CLIENT_SECRET=your_google_client_secret
export STRIPE_SECRET_KEY=your_stripe_secret_key
export STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### 4. Install Dependencies and Run

```bash
pip install -r requirements.txt
python main.py
```

## Usage

1. Visit `http://localhost:5001` and click "Login" to authenticate with Google
2. After login, you'll see your dashboard with current coin balance (starts with 100 coins)
3. Click "Buy Coins" to purchase additional coins via Stripe checkout
4. Complete the payment using Stripe's test card: `4242 4242 4242 4242`
5. Coin balance updates automatically after successful payment via webhook

**Note**: This example uses an in-memory database, so user data is lost when the app restarts. For production use, change the database connection to use a persistent file or external database.