# OAuth Examples

This directory contains some examples of OAuth in action. See the [docs](https://docs.fastht.ml/explains/oauth.html) for a more detailed explanation.

- minimal.py - initializes an OAuth client and retrieves the user's profile, displaying it in the browser after a successful login.
- oa.py - a minimal example showing use of the OAuth class, gating access to the homepage to users who belong to the Google domain "answer.ai"
- database.py - a legacy example used in an OAuth explanation, not recommended for use.


These examples require two environment variables to be set. Run with:

```
export AUTH_CLIENT_ID=your_client_id
export AUTH_CLIENT_SECRET=your_client_secret
python minimal.py
```
