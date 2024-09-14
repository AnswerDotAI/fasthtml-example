from fasthtml.common import *
from datetime import datetime

app,rt = fast_app(hdrs=[sid_scr], live=True)

@rt
def index():
    return Titled('Session storage test',
                  P('Create multiple tabs or windows and click the button in each a few times'),
                  Button(hx_get=more, target_id="foo")('Click'),
                  Div(id='foo'))

@rt
async def more(sid:str): return f'{sid}: {datetime.now()}'

serve()

