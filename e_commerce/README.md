# Complete App Example

A full-featured [FastHTML](https://github.com/AnswerDotAI/fasthtml) application demonstrating [OAuth](https://fastht.ml/docs/explains/oauth.html) authentication, database integration with [FastLite](https://github.com/AnswerDotAI/fastlite), and Stripe payment processing with a credit-based system via [FastStripe](https://github.com/AnswerDotAI/faststripe).

## Setup

### 1. Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
4. Configure the OAuth consent screen if prompted
5. Set Application type to "Web application"
6. Add `http://localhost:5001/redirect` to "Authorized redirect URIs"
7. Copy the Client ID and Client Secret

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