from fasthtml.common import *
from datetime import datetime

app,rt = fast_app()

def keytrig(key, mods=None, **kw):
    keyup = '&&'.join(listify(mods)+[f"event.key==='{key}'"])
    return {'hx_trigger': f"click, keyup[{keyup}] from:body"} | kw

@rt
async def more(): return datetime.now()

@rt
def index():
    return Titled('Keyboard demo',
        Div(id='targ'),
        Button('Time', hx_get=more, hx_target='#targ', **keytrig('r'))
    )

serve()

