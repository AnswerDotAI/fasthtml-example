from fasthtml.common import *
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI
import os, openai, time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

style = Style("""
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; }
    .article { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
    .article h2 { margin-top: 0; }
    .article img { max-width: 100%; height: auto; }
    .article a { color: #3498db; text-decoration: none; }
    .article a:hover { text-decoration: underline; }
"""),

app = FastHTML(hdrs=(style))
rt = app.route

# Database setup
db = database('distilhn.db')
summaries = db.t.summaries
if summaries not in db.t:
    summaries.create(url=str, title=str, summary=str, image_url=str, hn_comments=str, created_at=float, pk='url')
Summary = summaries.dataclass()

def Article(s):
    return Div(
        H2(A(s.title, href=s.url)),
        Img(src=s.image_url) if s.image_url else None,
        P(s.summary),
        P(A("HN Comments", href=s.hn_comments)),
        cls="article",
    )


@rt("/")
async def get():
    """Main page with summaries"""
    latest_summaries = summaries(order_by='-created_at', limit=20)
    return Title("CoolHN"), Body(
        H1("AI Summarized Hacker News"),
        P("Front-page articles summarized hourly."),
        *(Article(s) for s in latest_summaries),
        cls='container')


sp = """You are a helpful assistant that summarizes articles. Given an article text, possibly including unrelated scraping artefacts, return a summary of the article. If the text is just something like 'enable javascript' or 'turn off your ad blocker', just respond with "Could not summarize article." Otherwise, respond with just the summary (no preamble). Favour extremely conciseness and brevity. Start directly with the contents. Aim for <100 words."""
async def summarize_text(text):
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": sp
        }, {
            "role": "user",
            "content": f"Please summarize the following text: {text}"
        }],
        model="gpt-4o-mini",
    )

    summary = chat_completion.choices[0].message.content.strip()
    return summary


async def fetch_hn_stories():
    """Fetch latest HN stories using aiohttp"""
    async with aiohttp.ClientSession() as session, session.get(
            'https://hacker-news.firebaseio.com/v0/topstories.json'
    ) as response:
        story_ids = await response.json()
        stories = []
        for story_id in story_ids[:30]:
            async with session.get(
                    f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
            ) as story_response:
                story = await story_response.json()
                if 'url' in story:
                    stories.append(story)
        return stories


async def process_article(url, title, hn_comments):
    """Fetch and process a single article"""
    # Check if URL has already been summarized
    existing_summary = summaries(where=f"url='{url}'")
    if existing_summary:
        return existing_summary[0]

    # Fetch article content
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract image
                og_image = soup.find('meta', property='og:image')
                image_url = og_image['content'] if og_image else None

                # Check that image URL resolves
                if image_url:
                    async with session.get(image_url,
                                           timeout=3) as image_response:
                        if image_response.status != 200:
                            image_url = None

                # Extract main text (https://pypi.org/project/html2text/ may be better)
                for tag in soup(["script", "style"]):
                    tag.decompose()
                text = ' '.join(soup.stripped_strings)

                # Summarize
                summary = await summarize_text(text)
                print(f"Summary for {url}:\n", summary)

                # Save to database
                summaries.upsert(
                    Summary(url=url,
                            title=title,
                            summary=summary,
                            image_url=image_url,
                            hn_comments=hn_comments,
                            created_at=time.time()))
        except aiohttp.ClientError as e:
            print(f"Network error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# In a thread we fetch the latest HN stories every hour
async def update_summaries():
    while True:
        try:
            stories = await fetch_hn_stories()
        except:
            print("Failed to fetch HN stories", e)
            await asyncio.sleep(3600)
            continue
        for story in stories:
            await process_article(
                story['url'], story['title'],
                f"https://news.ycombinator.com/item?id={story['id']}")
        await asyncio.sleep(3600)  # Update every hour


@app.on_event("startup")
async def start_update_task():
    asyncio.create_task(update_summaries())


serve()