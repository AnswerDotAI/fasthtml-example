import httpx
from fastcore.utils import *
from fastcore.script import *

def get_client(cookie_file):
    client = httpx.Client()
    cookies = Path(cookie_file).read_json()
    for k,v in cookies.items(): client.cookies.set(k, v)
    return client

@call_parse
def auth_cli(
    host='localhost:5001', # token server host
    token_file='auth_token.txt' # file to load token from
):
    "Test doing some authenticated action in the CLI"
    client = get_client(token_file)
    url = f'http://{host}/secured'
    res = client.get(url).text
    print(res)

