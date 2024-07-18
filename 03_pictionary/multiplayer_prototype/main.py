from fasthtml.common import *
import anthropic, os, base64, uvicorn, uuid
import time
import random
from collections import OrderedDict, deque
import google.generativeai as genai
from openai import AzureOpenAI
from PIL import ImageDraw, ImageFont
from PIL import Image as PILImage
import asyncio
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import threading

# Website (no "/")
domain = "https://ai-pictionary.up.railway.app"

# Wordlist
words = ['lips', 'caterpillar', 'ants', 'jellyfish', 'cupcake', 'seashell', 'grass', 'island', 'coat', 'bee', 
 'eye', 'lion', 'car', 'bus', 'boy', 'knee', 'bathroom', 'ball', 'jacket', 'flag', 'snowflake', 'football', 
 'grapes', 'bumblebee', 'music', 'book', 'lemon', 'dragon', 'dream', 'eyes', 'balloon', 'triangle', 'sunglasses', 'zebra', 
 'feet', 'ant', 'bed', 'rocket', 'river', 'candle', 'float', 'smile', 'alligator', 'bunny', 'plant', 'snake', 'bird', 'duck', 
 'kitten', 'earth', 'starfish', 'ear', 'monkey', 'lollipop', 'sun', 'branch', 'blanket', 'orange', 'carrot', 'cube', 'dinosaur', 
 'hippo', 'candy', 'jail', 'cow', 'drum', 'hamburger', 'hat', 'light', 'inchworm', 'snail', 'cat', 'shirt', 'nose', 'alive', 
 'person', 'jar', 'tail', 'motorcycle', 'whale', 'zigzag', 'suitcase', 'backpack', 'feather', 'line', 'mitten', 'woman', 'robot', 
 'cheese', 'chimney', 'comb', 'egg', 'worm', 'zoo', 'pizza', 'fly', 'pen', 'coin', 'apple', 'baseball', 'oval', 'skateboard', 'frog', 
 'spoon', 'horse', 'beach', 'slide', 'ladybug', 'window', 'rabbit', 'helicopter', 'desk', 'head', 'leg', 'crayon', 'clock', 'boat', 
 'diamond', 'bug', 'ears', 'box', 'face', 'night', 'square', 'pie', 'bear', 'finger', 'banana', 'mouth', 'nail', 'cherry', 'bike', 
 'broom', 'fire', 'sea', 'beak', 'baby', 'bowl', 'popsicle', 'lamp', 'blocks', 'bark', 'elephant', 'spider', 'rock', 'purse', 'leaf', 
 'ship', 'shoe', 'kite', 'mountains', 'moon', 'table', 'rain', 'sheep', 'curl', 'daisy', 'snowman', 'train', 'legs', 'swing', 'mountain', 
 'cup', 'truck', 'flower', 'glasses', 'crab', 'owl', 'ring', 'love', 'lizard', 'door', 'heart', 'button', 'giraffe', 'chicken', 
 'chair', 'bridge', 'key', 'neck', 'ghost', 'computer', 'bow', 'bread', 'corn', 'water', 'angel', 'fork', 'bone', 'candy', 'roof', 
 'underwear', 'drum', 'spider', 'shoe', 'smile', 'cup', 'hat', 'bird', 'kite', 'snowman', 'doll', 'skateboard', 'sleep', 'sad', 
 'butterfly', 'elephant', 'ocean', 'book', 'egg', 'house', 'dog', 'ball', 'star', 'shirt', 'cookie', 'fish', 'bed', 'phone', 'airplane', 'nose', 
 'apple', 'sun', 'sandwich', 'cherry', 'bubble', 'moon', 'snow', 'rocket', 'cliff', 'stingray', 'horse', 'sack', 'paper', 'drumstick', 'teapot', 
 'plug', 'button', 'cave', 'crumb', 'children', 'bib', 'panda', 'unite', 'eel', 'cocoon', 'cook', 'city', 'stove', 'apologize', 'maze', 
 'sunset', 'step', 'organ', 'jump', 'ribbon', 'pizza', 'pop', 'tape', 'pot', 'table', 'calendar', 
 'squirrel', 'letter', 'coconut', 'napkin', 'hero', 'newborn', 'doghouse', 'baby', 'turkey', 'cheetah', 'sidekick', 
 'cucumber', 'crust', 'sunglasses', 'computer', 'scar', 'stick', 'grill', 'rat', 'teacher', 'farm', 'tusk',
 'lung', 'lock', 'refrigerator', 'ambulance', 'ship', 'harmonica', 'soda', 'eagle', 'rainstorm', 'hoof', 'fern', 
 'platypus', 'pitchfork', 'pinecone', 'pencil', 'parent','trombone', 'midnight', 'sap', 'pharaoh','panda']

# AI clients
genai.configure(api_key=os.environ.get("G_API_KEY"))
openai_client = AzureOpenAI(
  azure_endpoint='https://answeroai-eus2.openai.azure.com',
  api_key=os.environ.get("AZURE_KEY"),
  api_version="2024-02-01",
)
anthropic_client = anthropic.Anthropic(
  api_key=os.environ.get("ANTHROPIC_API_KEY"), )

# Game params
game_time = 30
max_game_age = game_time + 5
max_active_games = 2

# Database setup
db = database('data/pictionary.db')
games, guesses, images = db.t.games, db.t.guesses, db.t.images
if games not in db.t:
  games.create(id=int, word=str, start_time=float, end_time=float, drawer_id=str, 
               status=str, nickname=str, last_image=str, gif_path=str, pk='id')
  images.create(id=int, image=str, game_id=int, time=float, pk='id')
  guesses.create(id=int, game_id=int, player_id=int, word=str, image_id=str,
                 guess=str, guesser_name=str, guesser_id=str, time=float, pk='id')
Game, Guess, Image = games.dataclass(), guesses.dataclass(), images.dataclass()
if not os.path.exists('data/images'): os.mkdir('data/images')

# Queue for players waiting to start a game
player_queue = OrderedDict()

# Beforeware to set session id
def before(session):
  if not 'sid' in session: session['sid'] = str(uuid.uuid4())
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/data/images/.*'])

# Main Application
js = Script(open('multiplayer.js').read())
css = Style(open('multiplayer.css').read(), type="text/css", rel="stylesheet")
htmx = Script(src="https://unpkg.com/htmx.org@next/dist/htmx.min.js")
sakura = Style(open('sakura.css').read(), type="text/css", rel="stylesheet")
confetti = Script(src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js")
app = FastHTML(before=bware,hdrs=(htmx, sakura, js, css, MarkdownJS(), confetti),
               default_hdrs=False, key_fname='data/.sesskey')

# Game Management
class GameManager:

  def __init__(self):
    self.active_games = {}
    self.recent_guesses = {}
    self.word_list = words

  def start_game(self, drawer_id):
    word = random.choice(self.word_list)
    game = games.insert(
        Game(id=None, word=word, start_time=time.time(), end_time=None,
             drawer_id=drawer_id, status='active', last_image=None))
    self.active_games[game.id] = game
    self.recent_guesses[game.id] = deque(maxlen=10)
    print("Starting game", game)
    return game

  def end_game(self, game_id):
    game = games[game_id]
    game.end_time = time.time()
    game.status = 'completed'
    games.update(game)

    gif_path = self.create_game_gif(game_id)  # Create the GIF
    if gif_path and "None" not in gif_path:
      game.gif_path = gif_path  # Add this line to store the GIF path
      games.update(game)  # Update the game record with the GIF path

    del self.active_games[game_id]
    del self.recent_guesses[game_id]
    print("Ended", game)

  # Make a GIF of a game
  def create_game_gif(self, game_id):
    game_images = images(where=f'game_id={game_id}')
    game_guesses = guesses(where=f'game_id={game_id}')
    frames = []
    for i, img in enumerate(game_images):
      frame = PILImage.new('RGB', (840, 512), color='white')
      game_img = PILImage.open(img.image).resize((512, 512))
      frame.paste(game_img, (0, 0))
      draw = ImageDraw.Draw(frame)
      font = ImageFont.truetype(
          "font.ttf", 20)
      y_offset = 10
      has_guesses = False
      for guess in game_guesses:
        if guess.image_id == img.image:
          text = f"{guess.guesser_name}: {guess.guess}"
          draw.text((532, y_offset), text, font=font, fill='black')
          y_offset += 30
          has_guesses = True
      if has_guesses:
        frames.append(frame)
      if i == len(game_images) - 1:
        text = "Word was: " + games[game_id].word
        draw.text((532, y_offset), text, font=font, fill='black')
        frames.append(frame)

    # Save the frames as a GIF
    if not frames: return None
    if len(frames) <= 1: return None
    gif_path = f"data/images/game_{game_id}.gif"
    frames[0].save(gif_path,save_all=True,append_images=frames[1:],
                   duration=1000,loop=0)

    return gif_path
gm = GameManager()

# Main page. Shows active games count and active area,
# which is where the user can start a new game / join the queue
# and where the game will be displayed.
@app.get("/")
def home(session):
  return Title("AI Pictionary"), Navbar(), Main(
      P("Show off your drawing skills as AIs try to guess what you're drawing! Or check out the ",
        A("leaderboard", href="/leaderboard"),
        "to see the times to beat..."),
      # active_game_count(),
      active_area(session),
      # Div("""Well, that went on without vandalism longer than expected. We may resume another day :)""", cls="marked"),
      cls='container')

def Navbar(page=None):
  return Nav(
            Div(
              H3(A('<- Home', href='/') if page else 'AI Pictionary'),
              cls='navbar-brand'
            ),
            Div(
              A('Spectate', href='/spectate' if page != 'spectate' else '#'),
              A('Leaderboard', href='/leaderboard' if page != 'leaderboard' else '#'),
              A('About', href='/about' if page != 'about' else '#'),
              cls='navbar-links'
            ),
            cls='navbar'
          )

# Simple markdown about page
@app.get("/about")
def about():
  return Title("About"), Navbar("about"), Main(
    
      Div(""" ## About
          
This was born from a demo that got a little out of control. I wanted to see if any of these multi-modal
LLMs could play pictionary. It turns out they can! And it's rather fun...

### Technical Details
          
This app is built with a new framework we're working on. More details soon...
          
The canvas (HTML/JS) sends images to the backend, which ships them off to a few different models to guess the word.
          
### Future Plans
          
I think this will be a fun, quirky eval for models. I'm saving all the drawings (I hope you don't draw anything bad) and the progressions
will make a good classification problem. Can a model guess from the final image? from the sequence? etc...

""", cls='marked'),
      A("Back to Home", href="/"),
      cls='container')

# Leaderboard table
@app.get("/leaderboard")
def leaderboard():
  fastest_games = games(where="status='completed' AND end_time IS NOT NULL",
                        order_by="(end_time - start_time) ASC",
                        limit=10)

  rows = []
  for i, game in enumerate(fastest_games, 1):
    duration = game.end_time - game.start_time
    player_name = game.nickname if game.nickname else "Anonymous"
    rows.append(
        Tr(Td(str(i)), Td(player_name), Td(game.word),
           Td(f"{duration:.2f} seconds"),
           Td(A("View", href=f"/game-summary?game_id={game.id}"))))

  table = Table(Thead(
      Tr(Th("Rank"), Th("Player"), Th("Word"), Th("Duration"),
         Th("Details"))),
                Tbody(*rows),
                cls="table table-striped table-hover")

  return Title("Leaderboard - Fastest Games"),  Navbar("leaderboard"),  Main(
      H1("Leaderboard: Top 10 Fastest Games"),
      table,
      A("Back to Home", href="/"),
      cls='container')

# Spectate page (shows live and historical games)
@app.get("/spectate")
def spectate():
  return Title("Spectate"), Navbar('spectate'), Main(
    H3("Active Games"),
    active_games_area(),
    H3("Past Games"),
    past_games_area(),
    cls='container')

# Active area (will later poll when queing hence separate route)
@app.get("/active_area")
def active_area(session):

  # If there's a queue and a free game, start a game with the first player in the queue
  if player_queue and len(gm.active_games) < max_active_games:
    player_id, _ = player_queue.popitem(last=False)
    gm.start_game(player_id)

  # If they're in an active game, show the game area
  if gm.active_games and session['sid'] in [game.drawer_id for game in gm.active_games.values()]:
    game_id = [game.id for game in gm.active_games.values() if game.drawer_id == session['sid']][0]
    game = gm.active_games[game_id]
    return Div(H2(f"Game {game_id}"),
               P(f"Your word is: {game.word}"),
               countdown(game.start_time),
               Canvas(id="drawingCanvas", width="512", height="512"),
               Div(H3("Guesses"), recent_guesses(session)),
               cls='container',
               id="active-area")

  # If they're in the queue, show the queue status (will poll every second for updates)
  if session['sid'] in player_queue:
    player_queue[session['sid']]['last_request'] = time.time(
    )  # Update last request time so they don't get pruned
    return Div(
        P("Game(s) full. You have been added to the queue."),
        P(f"You are #{list(player_queue.keys()).index(session['sid'])+1} in the queue."),
        P(f'There are {len(player_queue)} players in the queue in total.'),
        P(f"Estimated wait time:{game_time*len(player_queue)/max_active_games} seconds."),  # TODO better estimate
        hx_trigger="every 1s", hx_get="/active_area",
        hx_target="#active-area", hx_swap="outerHTML",
        id="active-area")

  # If they're not in an active game or the queue, show the start game button
  return Div(P(""),
             Form(Button("Play A Game!",type="submit"),hx_post="/join",
                  hx_target="#active-area",hx_swap="outerHTML"),
             id="active-area")


# Shows any recent guesses to the drawer (inserted into active area)
@app.get("/recent_guesses")
def recent_guesses(session):
  # If not in an active game return none
  if not gm.active_games or not session['sid'] in [game.drawer_id for game in gm.active_games.values()]:
    return None

  # Get the recent guesses for the active game
  game_id = [game.id for game in gm.active_games.values() if game.drawer_id == session['sid']][0]
  if not game_id in gm.recent_guesses: return None
  recent_gs = list(gm.recent_guesses[game_id])[::-1]
  if recent_gs:
    if any(g['guess'] == gm.active_games[game_id].word for g in recent_gs):
      print("Game over! Found a match.")
      gm.end_game(game_id)
      url = f"/game-summary?game_id={game_id}&celebrate=true"
      response = Response()
      response.headers['HX-Redirect'] = url
      return response

    return Div(
        *[P(f"{g['guesser_name']} guessed '{g['guess']}'") for g in recent_gs],
        id="guesses",
        hx_get=f"/recent_guesses",
        hx_target="#guesses",
        hx_trigger="every 1s",
        hx_swap="outerHTML")
  return Div("No guesses yet",
             id="guesses",
             hx_get=f"/recent_guesses",
             hx_target="#guesses",
             hx_trigger="every 1s",
             hx_swap="outerHTML")


# Ends game (if one running for this player) and redirects to summary
@app.get("/end-game")
def end_game(session):
  # Check if there's an active game
  if not gm.active_games or not session['sid'] in [
      game.drawer_id for game in gm.active_games.values()
  ]:
    return Title("No active game"), Main(H1("No active game"),
                                         A("home", href="/"),
                                         cls='container')
  # End the game and redirect to summary
  game_id = [
      game.id for game in gm.active_games.values()
      if game.drawer_id == session['sid']
  ][0]
  gm.end_game(game_id)     
  return RedirectResponse(f"/game-summary?game_id={game_id}")

# The summary of a game, with guess history, share link, etc.
@app.get("/game-summary")
def game_summary_page(game_id: int, session, celebrate:bool = False):
  game = games[game_id]
  gs = [Li(f"{guess.guesser_name} guessed: {guess.guess}" + (" (correct!)" if guess.guess == game.word else "")) for guess in guesses(where=f'game_id={game_id}')]
  gs.reverse()
  num_guesses = len(gs)
  gs = Ul(*gs) if num_guesses > 0 else P("No guesses yet.")

  # Prompt for a nickname if they haven't set one yet
  nickname_form = ""
  if session['sid'] == game.drawer_id and not game.nickname and 'nickname' not in session:
    nickname_form = Form(Input(type="text",name="nickname",laceholder="Enter your nickname"),
                         Input(type="submit", value="Save Nickname"),
                         hx_post=f"/save-nickname/{game_id}",
                         hx_target="#nickname-area")
  if session['sid'] == game.drawer_id and 'nickname' in session and not game.nickname:
    game.nickname = session['nickname']
    games.update(game)

  twitter_share = ""
  if session['sid'] == game.drawer_id:
    # Create Twitter share button
    share_text = f"I just drew '{game.word}' in {game.end_time - game.start_time:.2f} seconds on AI Pictionary! Can you beat my time?"
    share_url = domain + f"/game-summary?game_id={game_id}"
    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    twitter_share = A(Button("Share on Twitter"),
                      href=twitter_url,
                      target="_blank",
                      cls="btn btn-primary twitter-share-button")

  preview = ""
  if game.gif_path:
    preview = P(Img(src=f"/{game.gif_path}", width=840, height=512))
  elif game.last_image:
    preview = P(Img(src=f"/{game.last_image}", width=512, height=512))


  # Twitter meta tags
  metas = [
      Meta(name="twitter:card", content="summary_large_image"),
      Meta(name="twitter:site", content="@johnowhitaker"),
      Meta(name="twitter:title", content=f"Game {game_id} Summary"),
      Meta(name="twitter:description", content=f"Word: {game.word}"),
      Meta(name="twitter:image", content=f"{domain}/{game.gif_path}" if game.gif_path else f"{domain}/{game.last_image}"),
  ]
  main = Main(
        H3(f"Game {game_id} Summary"),
        P(f"Word: {game.word}"),
        P(f"Number of guesses: {num_guesses}"),
        P(f"Game duration: {game.end_time - game.start_time:.2f} seconds")
        if game.end_time else P("Game still active."),
        Div(P(f"Player: {game.nickname}" if game.nickname else ""),
            nickname_form,
            style="max-width: 500px;",
            id="nickname-area"),
        P(
            twitter_share,
            A(Button("Back to Home"), href="/"),
            A(Button("View Leaderboard"), href="/leaderboard", cls="btn btn-primary"),
        ) if session['sid'] == game.drawer_id else "",
        preview,
        gs,
        cls='container'
      )
  c = Script("""window.addEventListener('load', function() {
    window.confetti(ticks=100);
  });""") if celebrate else ""
  return Html(
    Head(confetti, c, htmx, sakura, js, css, *metas, Title(f"Game {game_id} Summary")), 
    Body(Navbar("summary"), main)
  )

# In the summary page, you can set a nickname for the leaderbaord
@app.post("/save-nickname/{game_id}")
def save_nickname(game_id: int, nickname: str, session):
  game = games[game_id]
  if session['sid'] == game.drawer_id:
    game.nickname = nickname
    games.update(game)
    session['nickname'] = nickname
    return P(f"Player: {game.nickname}")
  else:
    return P("You are not authorized to set a nickname for this game.")

# Active games count (updates every 5 seconds) - not used any more
@app.get("/active-games-count")
def active_game_count():
  return P(f"There are currently {len(gm.active_games)} ongoing games.",
           A("View Active Games", href="/active-games")
           if len(gm.active_games) > 0 else "",
           id="active_games_count",
           hx_trigger="every 5s",
           hx_get="/active-games-count",
           hx_target="#active_games_count",
           hx_swap="outerHTML")

#Spectate Mode utilities for showing active games (polling to update) and past games with a 'load more' button
def game_summary(game):
    return Div(
        H3(f"Game {game.id}"),
        P(f"Word: {game.word}"),
        P(f"Drawer: {game.drawer_id}"),
        P(f"Status: {game.status}"),
        P(f"Start time: {game.start_time}"),
        P("No images yet") if not game.last_image else Img(
            src=f"/{game.last_image}", width=256, height=256),
        P(f"Recent guesses: {[d['guess'] for d in list(gm.recent_guesses[game.id])]}"),
    )
@app.get("/active-games-area")
def active_games_area():
    gids = [game.id for game in gm.active_games.values()]
    if  gids:
      content = Div(*[game_summary(games[gid]) for gid in gids])
    else:
      content = P("No active games.")
    return Div(content,
             hx_trigger="every 3s", hx_get="/active-games-area",
             hx_target="#active-games-area", hx_swap="outerHTML",
             id="active-games-area")
@app.get("/past-games-area")
def past_games_area(page:int=1):
   # Infinite scroll sort of deal
    games_list = games(where="status='completed'", order_by="end_time DESC", limit=10, offset=(page-1)*10)
    content = Div(*[Img(src=f"{domain}/{game.gif_path}", alt=f"game {game.id}") for game in games_list if game.gif_path], id="past-games")
    new_btn = Button("Load More", hx_get=f"/past-games-area?page={page+1}", hx_target="#past-games", hx_swap="beforeend",
                     id="load-more", hx_swap_oob="outerHTML"),
    return content, new_btn
   

# JS: Countdown timer that navigates to /end-game when time is up
def countdown(start_time):
  elapsed_time = time.time() - start_time
  time_left = game_time - elapsed_time
  return Div(
      P(f"Time left: {time_left:.0f} seconds", id="time-left"),
      Script("""
setInterval(() => {
    let timeLeft = document.getElementById("time-left");
    let time = parseInt(timeLeft.innerText.split(":")[1]);
    time -= 1;
    timeLeft.innerText = `Time left: ${time} seconds`;
    if (time <= 0) {
        //navigate to /end-game if we're currently on "/"
        if (window.location.pathname === "/") {
               window.location.href = "/end-game";
        }
    }
}, 1000);
"""))


# They clicked "Join" to start a game
# - updates active area with a canvas + countdown
@app.post("/join")
def start_game(session):

  # If games are all full, add to queue (or show place in queue if already in it)
  if len(gm.active_games) >= max_active_games:
    if session['sid'] not in player_queue:
      player_queue[session['sid']] = {'last_request': time.time()}

  # There are free games
  else:
    # If there's a queue, start a game with the first player in the queue
    if player_queue:
      player_id, _ = player_queue.popitem(last=False)
      gm.start_game(player_id)
    # Otherwise, start a game with the current player
    gm.start_game(session['sid'])

  return active_area(session)


# Get the image from a canvas and process it
@app.post("/process-canvas")
def process_canvas(image: str, session):
  if not gm.active_games or session['sid'] not in [game.drawer_id for game in gm.active_games.values()]:
    return {"active_game": "no"}
  game_id = [game.id for game in gm.active_games.values() if game.drawer_id == session['sid']][0]
  image_bytes = image.file.read() # TODO async
  fn = f"data/images/{uuid.uuid4()}.png"
  with open(fn, 'wb') as f:
    f.write(image_bytes)
  images.insert(Image(image=fn, game_id=game_id, time=time.time()))
  game = games[game_id]
  game.last_image = fn
  games.update(game)
  gm.active_games[game_id].last_image = fn
  return {'active_game': 'yes', 'latest_image': fn}


## Guess functions ##
gpt4o_error_time = 0
def guess_gemini(image_fn, guess_history=None):
  prompt = "Guess the pictionary prompt. Reply with a single word only."
  if guess_history:
    prompt += f"\nPast guesses: {', '.join([g['guess'] for g in guess_history])}"
  img = PILImage.open(image_fn)
  model = genai.GenerativeModel('gemini-1.5-flash') # ('models/gemini-1.5-pro')  #
  response = model.generate_content([prompt, img])
  response.resolve()
  return "Flash 1.5", response.text
def guess_gpt_4o(image_fn, guess_history=None):
  global gpt4o_error_time
  prompt = "Guess the pictionary prompt. Reply with a single word only."
  if guess_history:
    prompt += f"\nPast guesses: {', '.join([g['guess'] for g in guess_history])}"
  base64_image = base64.b64encode(open(image_fn, 'rb').read()).decode('utf-8')
  if time.time() - gpt4o_error_time < 3:
    time.sleep(3)
    return "GPT-4o", "rate limited, waiting a bit"
  try:
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
            "user",
            "content": [{
                "type": "text",
                "text": prompt
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }]
        }])
    return "GPT-4o", completion.choices[0].message.content
  except Exception as e:
    # Check for AzureOpenAI.RateLimitError
    if "RateLimitError" in str(e):
      gpt4o_error_time = time.time()
      return "GPT-4o", "rate limited, try again later"+str(e)
    return "GPT-4o", f"Error: {str(e)}"
def guess_haiku(image_fn, guess_history=None):
  prompt = "Guess the pictionary prompt. Reply with a single word only."
  if guess_history:
    prompt += f"\nPast guesses: {', '.join([g['guess'] for g in guess_history])}"
  image_bytes = open(image_fn, "rb").read()
  image_base64 = base64.b64encode(image_bytes).decode('utf-8')
  message = anthropic_client.messages.create(
      model="claude-3-haiku-20240307",
      max_tokens=100,
      temperature=0.5,
      messages=[{
          "role":
          "user",
          "content": [{
              "type": "image",
              "source": {
                  "type": "base64",
                  "media_type": "image/png",
                  "data": image_base64,
              },
          }, {
              "type": "text",
              "text": prompt
          }],
      }],
  )
  caption = message.content[0].text
  return "Haiku", caption
def random_guess(image_fn, guess_history=None):
  if guess_history:
    all_guesses = [g['guess'] for g in guess_history]
    print("(random) all past guesses:)", all_guesses)
  return random.choice(["apple", "house", "cat", "sun", "tree"])

class ImprovedGuessSystem:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.guess_queue = asyncio.Queue()
        self.last_guess_times = {}
        self.executor = ThreadPoolExecutor(max_workers=10)  # Adjust based on your needs
        self.running = False
        self.loop = None

    def start_background_task(self):
        self.running = True
        thread = threading.Thread(target=self.run_async_loop, daemon=True)
        thread.start()

    def run_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())

    async def start(self):
        await asyncio.gather(
            self.queue_manager(),
            self.guess_worker()
        )

    async def queue_manager(self):
        while self.running:
            for game_id, game in self.game_manager.active_games.items():
                if game and game.status == 'active' and game.last_image:
                    current_time = time.time()
                    last_guess_time = self.last_guess_times.get(game_id, 0)
                    if current_time - last_guess_time >= 2:  # 2 second minimum wait
                        await self.guess_queue.put(game_id)
                        self.last_guess_times[game_id] = current_time
            await asyncio.sleep(0.1)  # Small delay to prevent tight looping

    async def guess_worker(self):
        async with aiohttp.ClientSession() as session:
            while self.running:
                game_id = await self.guess_queue.get()
                game = self.game_manager.active_games.get(game_id)
                if game and game.status == 'active' and time.time() - game.start_time > max_game_age:
                  print(f"Ending game {game.id} due to age.")
                  del gm.active_games[game_id]
                  await self.update_game(game_id)
                  continue
                if game and game.status == 'active':
                    await self.process_game(game, session)
                self.guess_queue.task_done()

    async def process_game(self, game, session):
        image = game.last_image
        guess_history = self.game_manager.recent_guesses[game.id]
        
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, guess_haiku, image, guess_history),
            loop.run_in_executor(self.executor, guess_gemini, image, guess_history),
            loop.run_in_executor(self.executor, guess_gpt_4o, image, guess_history)
        ]

        guesses = []
        try:
            done, _ = await asyncio.wait(tasks, timeout=5)
            for future in done:
                try:
                    result = future.result()
                    guesses.append(result)
                except Exception as e:
                    print(f"Error in guess for game {game.id}: {str(e)}")
        except asyncio.TimeoutError:
            print(f"Timeout for guesses in game {game.id}")

        await self.process_guesses(game, guesses)

    async def process_guesses(self, game, guesses):
        for guess in guesses:
            if game.id not in self.game_manager.recent_guesses:
              continue
            if "rate limited" in guess[1]:
              print("Rate limited, skipping guess.", guess)
              continue
            guesser_name, guess_text = guess
            guess_text = guess_text.strip().lower()
            guess_text = ''.join(e for e in guess_text if e.isalnum() or e.isspace())
            
            self.game_manager.recent_guesses[game.id].append({
                "guess": guess_text,
                "guesser_name": guesser_name
            })
            # Here you would insert the guess into your database
            # This should be done asynchronously as well
            await self.insert_guess_to_db(game.id, game.drawer_id, game.word, game.last_image, guess_text, guesser_name)


    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.executor.shutdown(wait=False)
    
    async def insert_guess_to_db(self, game_id, drawer_id, word, image, guess, guesser_name):
        d = database('data/pictionary.db')
        G = d.t.guesses.dataclass()
        d.t.guesses.insert(
            Guess(game_id=game_id,
                  player_id=drawer_id,
                  word=word,
                  image_id=image,
                  guess=guess,
                  guesser_name=guesser_name,
                  guesser_id="ai",
                  time=time.time())
        )
        d.close() # Yuk

    async def update_game(self, game_id):
        d = database('data/pictionary.db')
        G = d.t.games.dataclass()
        game = d.t.games[game_id]
        game.end_time = time.time()
        game.status = 'completed'
        d.t.games.update(game)
        d.close() # Yuk
        

# Start the guess loop
guess_system = ImprovedGuessSystem(gm)
guess_system.start_background_task()

# Prune players from the queue if they've not checked in for a while
@startthread
def queue_pruner():
  while True:
    for player_id in list(player_queue.keys()):
      if time.time() - player_queue[player_id]['last_request'] > 60:
        del player_queue[player_id]
        print(f"Removed {player_id} from queue.")
    time.sleep(1)

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
  return FileResponse(f'{fname}.{ext}')

if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', reload=True, port=int(os.getenv("PORT", default=5000)))