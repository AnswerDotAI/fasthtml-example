from fasthtml.common import *
from datetime import datetime

def before(sid:str=''): print(sid or '-')
app,rt = fast_app(hdrs=[sid_scr], before=Beforeware(before), live=True)

@rt
def content(sid:str=''):
    return Titled('Session storage test',
        P('Create multiple tabs or windows and refresh in each a few times'),
        Div(f'{sid}: {datetime.now()}', id='foo')
    )

with_sid(app, '/content')

serve()

