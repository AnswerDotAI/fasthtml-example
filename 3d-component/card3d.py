from fasthtml.common import *
# Based on surreal.js version: https://gist.github.com/gnat/f094e947b3a785e1ed6b7def979132ae
# ...which is based on this web component: https://github.com/zachleat/hypercard
# ...which is from this version: https://codepen.io/markmiro/pen/wbqMPa

def card_3d(text, background, amt=1., left_align=False):
    return Div(text, Div(), Style("""
me {
    position: relative; width: 300px; height: 400px; padding: 1em;
    font-weight: bold; text-align: %s; text-shadow: 0 0 4px #000; color: #ddd;
    box-shadow: 0 1px 5px #00000099; border-radius: 10px; background: url(%s) center/cover;
    transition: .3s ease-out; transition-property: transform, box-shadow; margin: 1em;
}
me:hover { transition-duration: .15s; box-shadow: 0 5px 20px 5px #00000044; }
me > div {
    position: absolute; inset: 0; border-radius: 10px;
    background-image: radial-gradient(circle at 90%% -20%%, #ffffff55, #0000000f);
}""" % ("left" if left_align else "right", background)),
        Script("""
me().on('mouseenter', ev => {
    let e = me(ev)
    e.bounds = e.getBoundingClientRect()
    e.on('mousemove', e.rotateToMouse)
}).on('mouseleave', ev => {
    let e = me(ev)
    e.off('mousemove', e.rotateToMouse)
    e.style.transform = e.style.background = ''
})
me().rotateToMouse = ev => {
    let e = me(ev), b = e.bounds
    let x = ev.clientX - b.x - b.width / 2
    let y = ev.clientY - b.y - b.height / 2
    let d = Math.hypot(x,y)
    let amt = %s
    e.style.transform = `scale3d(${1 + 0.07 * amt}, ${1 + 0.07 * amt}, 1.0)
                         rotate3d(${y/100*amt}, ${-x/100*amt}, 0, ${Math.log(d)*2*amt}deg)`
    me('div', e).style.backgroundImage = `radial-gradient(
        circle at ${x*2 + b.width/2}px ${y*2 + b.height/2}px, #ffffff77, #0000000f)`
}""" % amt))
