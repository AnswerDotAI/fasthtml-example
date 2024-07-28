from fasthtml.common import *
from card3d import card_3d
from playingcard import playing_card

hdrs = [Style('''* { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
    body { 
        font-family: 'Arial Black', 'Arial Bold', Gadget, sans-serif;
        perspective: 1500px; background: linear-gradient(#666, #222);
    }''')]
app = FastHTML(hdrs=hdrs)
rt = app.route

@rt('/')
def get():
    url1 = "https://images.unsplash.com/photo-1557672199-6e8c8b2b8fff"
    url2 = "https://ucarecdn.com/35a0e8a7-fcc5-48af-8a3f-70bb96ff5c48/-/preview/750x1000/"
    cards = [playing_card(*o) for o in [('clubs','jack'), ('hearts','queen'), ('spades','king')]]

    return Div(
        Div(card_3d('FastHTML', url1, 1.5, hx_get='/click'),
            card_3d('Components!', url2, 1.5, left_align=True, hx_get='/click')),
        Div(*cards)
    )

@rt('/click')
def get(): return P('Clicked!')

serve()
