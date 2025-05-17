from fasthtml.common import *

app = FastHTML(middleware=[cors_allow])
rt = app.route

@rt
def index(d:dict, q:str=""):
    print(str(d)[:1000])
    return q

serve()

