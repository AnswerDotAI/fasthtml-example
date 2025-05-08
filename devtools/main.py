from fasthtml.common import *
from pathlib import Path

hdrs = [Link(href="/static/styles.css", rel="stylesheet")]
app,rt = fast_app(hdrs=hdrs)
app.devtools_json()

@rt
def index():
    return Titled(
        'com.chrome.devtools.json demo',
        P('You can see the devtools json here: ', A(devtools_loc, href=devtools_loc))
    )

serve()

