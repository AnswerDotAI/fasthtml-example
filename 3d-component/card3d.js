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
    let amt = {amt}
    e.style.transform = `scale3d(${ 1 + 0.07 * amt }, ${ 1 + 0.07 * amt }, 1.0)
                         rotate3d(${ y/100*amt }, ${ -x/100*amt }, 0, ${ Math.log(d)*2*amt }deg)`
    me('div', e).style.backgroundImage = `radial-gradient(
        circle at ${ x*2 + b.width/2 }px ${ y*2 + b.height/2 }px, #ffffff77, #0000000f)`
}
