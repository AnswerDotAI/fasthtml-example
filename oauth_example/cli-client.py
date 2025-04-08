import secrets, httpx, webbrowser
from fastcore.utils import *
from time import time, sleep

def poll_token(paircode, host, interval=1, timeout=180):
    "Poll server for token until received or timeout"
    start = time()
    while time()-start < timeout:
        resp = httpx.get(f"http://{host}/token?paircode={paircode}").raise_for_status()
        if resp.text.strip(): return resp.text
        sleep(interval)

@call_parse
def auth_cli(
    host='localhost:5001', # token server host
    token_file='auth_token.txt' # file to save token to
):
    "Authenticate CLI with server and save token"
    paircode = secrets.token_urlsafe(16)
    url = f'http://{host}/cli_login?paircode={paircode}'
    login_url = httpx.get(url).text
    print(f"Opening browser for authentication...")
    webbrowser.open(login_url)
    token = poll_token(paircode, host)
    if token:
        Path(token_file).write_text(token)
        print(f"Authentication successful! Token saved to {token_file}")
    else: print("Authentication timed out")

