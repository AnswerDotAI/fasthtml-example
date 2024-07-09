from fasthtml.common import *
# Based on surreal.js version: https://gist.github.com/gnat/f094e947b3a785e1ed6b7def979132ae
# ...which is based on this web component: https://github.com/zachleat/hypercard
# ...which is from this version: https://codepen.io/markmiro/pen/wbqMPa

def card_3d(text, background, amt=1., left_align=False, **kw):
    scr = ScriptX('card3d.js', amt=amt)
    align='left' if left_align else 'right'
    sty = StyleX('card3d.css', background=f'url({background})', align=align)
    return Div(text, Div(), sty, scr, **kw)
