from fasthtml.common import *

def _card_bg(path):
    return f"url('https://tekeye.uk/playing_cards/images/svg_playing_cards/{path}.svg') center/cover"

def playing_card(suit, rank):
    "Create a flippable playing card component for any card"
    front = _card_bg(f'fronts/{suit}_{rank}')
    back = _card_bg('backs/blue2')
    return Div(
        Div(cls="front"), Div(cls="back"),
        StyleX('playingcard.css', front=front, back=back),
        Script("me().on('click', ev => me(ev).classToggle('flipped'))"),
        cls="playing-card")
