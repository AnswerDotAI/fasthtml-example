from fasthtml.common import *

app = FastHTML(middleware=[cors_allow])
rt = app.route

@rt
def index(q:str): return q

serve()

