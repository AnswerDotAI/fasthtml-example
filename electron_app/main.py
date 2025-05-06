# /// script
# requires-python = ">=3.12"
# dependencies = ['python-fasthtml']
# ///

from fasthtml.common import *

app, rt = fast_app()

@rt("/")
def get(): return P("Hello, World!")

serve()