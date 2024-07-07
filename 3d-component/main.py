from fasthtml.common import *
from card3d import card_3d

hdrs = (
    Style('''* { box-sizing: border-box; }
html, body { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
body { font-family: system-ui, sans-serif; perspective: 1500px; background: linear-gradient(#666, #222); }'''),
)
app = FastHTML(hdrs=hdrs)
rt = app.route

@rt('/')
def get():
    url = "https://images.unsplash.com/photo-1557672199-6e8c8b2b8fff?ixlib=rb-1.2.1&auto=format&fit=crop&w=934&q=80"
    return (card_3d('FastHTML', "https://i.postimg.cc/MHKFqnq6/1679116297740936.png", 2.),
        card_3d('Components!', url, 2., left_align=True))

run_uv()

