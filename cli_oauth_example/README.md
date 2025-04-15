# CLI Authentication with OAuth Example

This example shows how to implement OAuth authentication for CLI apps using FastHTML.
It allows users to authenticate with providers like Google and GitHub without manually copying tokens - similar to popular CLIs like GitHub and Railway.

## Files

- `server.py` - The server component that handles OAuth redirects and token management
- `client-login.py` - The client component that initiates login and stores the authentication token
- `client-do.py` - A client that uses the saved authentication to make requests

## Usage

1. Start the server:
   ```
   python server.py
   ```

2. In another terminal, run the client to authenticate:
   ```
   python client-login.py
   ```

3. A browser window will open for authentication
4. After successful login, the session cookies are saved to `auth_token.txt`
5. You can now make authenticated API calls using the saved session:
   ```
   python client-do.py
   ```

## How It Works

The authentication flow follows these steps:

1. **Client Initialization**: 
   - The client generates a random `paircode` as a unique identifier for this authentication session
   - This `paircode` connects the CLI process to the browser authentication flow

   ```python
   # From client-login.py
   paircode = secrets.token_urlsafe(16)
   ```

2. **Server Communication**:
   - The client sends the `paircode` to the server
   - The server stores this `paircode` temporarily and returns a login URL
   - The login URL includes the `paircode` as state parameter

   ```python
   # From client-login.py
   url = f'http://{host}/cli_login?paircode={paircode}'
   login_url = httpx.get(url).text
   ```

   ```python
   # From server.py
   @rt
   async def cli_login(request, paircode:str):
       pc_store[paircode] = None
       return cli.login_link(redir_url(request, redir_path), state=paircode)
   ```

3. **User Authentication**:
   - The client opens the login URL in the user's browser
   - The user authenticates with the OAuth provider
   - After approval, the provider redirects back with an authorization code (named `code` in the `server.py`)

   ```python
   # From client-login.py
   webbrowser.open(login_url)
   ```

4. **Authentication Processing**:
   - The server receives the authorization code and the state (`paircode`)
   - It exchanges the code for user authentication information
   - The server associates this auth ID with the original `paircode`
   - If the user is new, they are added to the database

   ```python
   # From server.py
   @rt(redir_path)
   async def redirect(request, code:str, state:str=None):
       redir = redir_url(request, redir_path)
       auth = cli.retr_id(code, redir)
       if state and state in pc_store:
           pc_store[state] = auth
           if auth not in users: users.insert(User(auth=auth))
           return 'complete'
       else: return f"Failed to find {state} in {pc_store}"
   ```

5. **Session Creation and Retrieval**:
   - The client polls the server asking for authentication using the `paircode`
   - Once available, the server creates a session with the auth ID and returns it
   - The client saves the session cookies locally for future authenticated requests

   ```python
   # From server.py
   @rt
   async def token(paircode:str, sess):
       if pc_store.get(paircode, ''):
           auth = pc_store.pop(paircode)
           sess['auth'] = auth
           return auth
   ```

   ```python
   # From client-login.py
   def poll_token(paircode, host, interval=1, timeout=180):
       "Poll server for token until received or timeout"
       start = time()
       client = httpx.Client()
       while time()-start < timeout:
           resp = client.get(f"http://{host}/token?paircode={paircode}").raise_for_status()
           if resp.text.strip(): return dict(client.cookies)
           sleep(interval)
           
   # Save the session cookies
   cookies = poll_token(paircode, host)
   if cookies:
       with open(token_file, 'w') as f: json.dump(cookies, f)
       print(f"Token saved to {token_file}")
   ```

6. **Using the Authentication**:
   - The client loads the saved session cookies
   - It applies them to HTTP requests to authenticate with the server
   - The server identifies the user based on the session cookie

   ```python
   # From client-do.py
   def get_client(cookie_file):
       client = httpx.Client()
       cookies = Path(cookie_file).read_json()
       client.cookies.update(cookies)
       return client

   client = get_client(token_file)
   url = f'http://{host}/secured'
   res = client.get(url).text
   print(res)
   ```

   ```python
   # From server.py - the secured endpoint
   @rt
   async def secured(sess):
       return sess['auth']
   ```

   When the `/secured` endpoint is called, it demonstrates authentication by retrieving the auth value from the session. This endpoint verifies and returns the user's identity (authentication) but doesn't implement authorization logic to control access. If the session doesn't contain an 'auth' value, the request would fail with a KeyError. To add authorization checks you could use FastHTML's OAuth class to manage access control.

For more detailed information about OAuth implementation in FastHTML, see the [OAuth documentation](https://fastht.ml/docs/explains/oauth.html).