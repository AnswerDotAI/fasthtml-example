from fasthtml.common import *
from functools import cache

app,rt = fast_app()

@cache
def home(): return Titled('Hello world', P('Greetings from FastHTML'))

@rt("/")
def get(): return home()

serve()

