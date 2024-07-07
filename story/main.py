from story import *

app,rt = get_app()

def footer():
    links = (A('items', href='/'), A('gallery', href='/gallery'))
    return Footer(Div(links, cls='inner'), cls='wrapper style1 align-center')
    
@rt("/")
def get():
    items = [
        ItemContent("One", "Lorem ipsum dolor sit amet.", icon="gem"),
        ItemContent("Two", "Vivamus malesuada, augue eget feugiat volutpat.", icon="save"),
        ItemContent("Three", "Praesent vitae odio eget diam aliquet bibendum.", icon="chart-bar")
    ]
    sub = "This is a demonstration of the Items element from the demo."
    wrapper = Wrapper("Items", sub, Item(items), style=1, align='center')
    return PageWrapper("Items Demo", wrapper, footer())

@rt("/gallery")
def get():
    xtra = A("Details", cls="button small")
    items = [
        ItemContent("Title 1", "Short description 1", "images/pic01.jpg", xtra=xtra),
        ItemContent("Title 2", "Short description 2", "images/pic02.jpg", xtra=xtra),
        ItemContent("Title 3", "Short description 3", "images/pic03.jpg", xtra=xtra),
    ]
    sub = "This is a demonstration of the Gallery element."
    wrapper = Wrapper("Gallery", sub, Gallery(items), style=1)
    return PageWrapper("Gallery Demo", wrapper, footer())

run_uv()
