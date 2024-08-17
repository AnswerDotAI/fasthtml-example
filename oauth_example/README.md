# OAuth Examples

This directory contains three examples of OAuth in action. See the [docs](https://docs.fastht.ml/explains/oauth.html) for a more detailed explanation.

- minimal.py - initializes an OAuth client and retrieves the user's profile, displaying it in the browser after a successful login.
- database.py - shows how you can store the user id in the session, and use it (in conjunction with some beforeware) to control access to certain routes and ensure that the user can only access their own data in a database.

Both of these examples require two environment variables to be set. Run with:

```
export AUTH_CLIENT_ID=your_client_id
export AUTH_CLIENT_SECRET=your_client_secret
python minimal.py
```