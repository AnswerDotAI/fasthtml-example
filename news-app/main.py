import feedparser
from fasthtml.common import *

css = Style(':root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}')
app = FastHTML(hdrs=(picolink, css))


class NewsType(Enum):
    TOP_STORIES = 1
    LATEST_STORIES = 2
    def get_rss_feed_url(news_type):
        if news_type == NewsType.TOP_STORIES:
            return "https://feeds.feedburner.com/ndtvnews-top-stories"
        else:
            return "https://feeds.feedburner.com/ndtvnews-latest"


def fetch_news(news_type):
    feed = feedparser.parse(NewsType.get_rss_feed_url(news_type))
    return feed.entries


def build_articles(entries: list):
    articles = list()
    for entry in entries:
        article = Article(
            Hgroup(Summary(Strong(entry.title)), P(entry.summary)),
            A("Read More", href=entry.link, target="_blank", rel="noopener noreferrer",
              cls="secondary")
        )
        articles.append((article, Hr()))
    return Div(*articles, cls="stack")


def build_top_nav():
    return Nav(
        Ul(Li(H2('SimpleNewsApp'))),
        Ul(Li(A('Top', href='/')), Li(A('Latest', href='/latest'))))


@app.route("/")
def get():
    entries = fetch_news(NewsType.TOP_STORIES)
    articles = build_articles(entries)
    return (Title("SimpleNewsApp"), Main(build_top_nav(), *articles, cls="container"))


@app.route("/latest")
def get():
    entries = fetch_news(NewsType.LATEST_STORIES)
    articles = build_articles(entries)
    return (Title("SimpleNewsApp"), Main(build_top_nav(), *articles, cls="container"))


serve()
