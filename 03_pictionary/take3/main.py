from fasthtml.common import *
from collections import OrderedDict, deque
import threading, time, signal, sys, pathlib, random, uuid, base64
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from dataclasses import dataclass

# Settings
max_concurrent_games = 2
game_max_duration = 30
# game_max_duration += 4 # 3...2...1...GO! in the JS before the canvas starts accepting input
thread_debug = False
domain = "https://moodle-game.com"

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

# App
def before(session):
  if not 'sid' in session: session['sid'] = str(uuid.uuid4())
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/data/images/.*'])
css = Style(open('multiplayer.css').read(), type="text/css", rel="stylesheet")
js = Script(open('multiplayer.js').read())
confetti = Script(src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js")
sakura = Style(open('modified_sakura.css').read(), type="text/css", rel="stylesheet")
# override sakura body max-width and center content
mod = Style("""
body { 
max-width: 960px; 
margin: 0 auto;
text-align: center;
}
""", type="text/css")
app = FastHTML(hdrs=[css, sakura, js, mod, confetti, MarkdownJS()], before=bware)

# Set up the database with the tables we need
db = database('pictionary.db')
games, guesses, drawings = db.t.games, db.t.guesses, db.t.drawings
if games not in db.t:
    games.create(id=int, word=str, player=str, last_drawing=float, start_time=float, end_time=float,
                 player_name=str, game_gif=str, approved=bool, pk='id')
    guesses.create(id=int, drawing_fn=int, game=int, guess=str,  guesser=str,
                   word=str, correct=bool, pk='id')
    drawings.create(id=int, fn=str, game=int, time=float, pk='id')
Game, Guess, Drawing = games.dataclass(), guesses.dataclass(), drawings.dataclass()
db_lock = threading.Lock() # Since we're multi-threading here
pathlib.Path('data/images').mkdir(parents=True, exist_ok=True)

# Player and game management
player_queue = OrderedDict()
active_games = []
recent_guesses = []
def start_game(player_id):
    word = random.choice(words)
    with db_lock:
        game = games.insert(Game(word=word, player=player_id, start_time=time.time()))
    active_games.append(game)

# ROUTES #

def Navbar(page="home"):
    navbar_script = Script("""
    document.querySelector('.navbar-toggle').addEventListener('click', function() {
        const navbarLinks = document.querySelector('.navbar-links');
        navbarLinks.classList.toggle('active');
        
        // Toggle aria-expanded attribute
        const expanded = this.getAttribute('aria-expanded') === 'true' || false;
        this.setAttribute('aria-expanded', !expanded);
    });
    """, type='text/javascript')

    nav = Nav(
        Div(
            Div(
                A('Moodle', href='/'),
                cls='navbar-title'
            ),
            Div(
                A('Gallery', href='/gallery') ,
                A('Leaderboard', href='/leaderboard'),
                A('Stats', href='/stats'),
                A('About', href='/about'),
                cls='navbar-links'
            ),
            cls='navbar-content'
        ),
        Button("☰",
            aria_label='Toggle Navigation',
            cls='navbar-toggle'
        ),
        Div(id="endgame"), # Hidden div for endgame redirect
        cls='navbar',
    )

    return Div(nav, navbar_script, cls='navbar-container')

@app.get('/')
def home(session):
  return Title("Moodle"), Body(
        Navbar(),
        Div(
            active_area(session),
            cls='content'
        ))

@app.get('/active_area')
def active_area(session, last_game_id:int=None):

    # Add any players in the queue to active games if there are free games
    while player_queue and len(active_games) < max_concurrent_games:
        player_id, _ = player_queue.popitem(last=False)
        start_game(player_id)

    # If the current player is in an active game, show the game area
    if active_games and session['sid'] in [game.player for game in active_games]:
        active_game = [game for game in active_games if game.player == session['sid']][0]
        return Div(
            H2("Now Drawing: " + active_game.word, id="active-header"),
            # P(f"Active game {active_game.id}"), # TODO
            P("Draw as best you can in the time remaining!", id="active-subheader"),
            Div(
                countdown(active_game.start_time),
                Div("NO GUESSES YET", id="latest-guess", cls="actitem latestguess",
                style="border: 10px solid green; width: 350px;"),
                Canvas(id="drawingCanvas", width="512", height="512", cls='actitem canvas'), # TODO style this
                Div(Div(B("Recent guesses:"), cls="guess", style="margin-bottom: 0.5rem;"),
                    Div(id="guess-area",
                        hx_trigger="every 0.3s", hx_get="/guesses", 
                        hx_target="#guess-area", hx_swap="afterbegin"),
                    style="border: 10px solid red; height: 512px; width: 350px; overflow-y: auto; text-align: left;",
                    cls="actitem guessarea",
                ),
                cls="actcontainer", 
            ),
            id="active-area")

    # If they're in the queue, show the queue status (will poll every second for updates)
    if session['sid'] in player_queue:

        # Update last request time so they don't get pruned
        player_queue[session['sid']]['last_request'] = time.time()  

        # Estimate time remaining until the player will play:
        remaining_times = [game_max_duration - (time.time() - game.start_time) for game in active_games]
        position_in_queue = list(player_queue.keys()).index(session['sid']) + 1
        if position_in_queue < max_concurrent_games:
            estimate = int(sorted(remaining_times)[position_in_queue - 1])
        else:
            estimate = game_max_duration * len(player_queue) / max_concurrent_games
        
        # Show the queue status # <<< TODO restyle
        status = Div(
            P("Game(s) full. You have been added to the queue."),
            P(f"You are #{list(player_queue.keys()).index(session['sid'])+1} in the queue."),
            P(f'There are {len(player_queue)} players in the queue in total.'),
            P(f"Estimated wait time:{estimate} seconds."),
            hx_trigger="every 1s", hx_get="/active_area",
            hx_target="#active-area", hx_swap="outerHTML",
            id="active-area")
        return status

    # TODO: show leaderboard form if they're a top scorer

    # show previous games and stats if they've played before ("Play Again")
    # last_game_id = 123 # for testing
    btn_style = "width:300px; margin: 0.5rem;"
    if last_game_id is not None:
        return Div(
                    P(""),
                    P(f"Game {last_game_id} finished in {games[last_game_id].end_time - games[last_game_id].start_time:.2f} seconds."),
                    Div(
                        Div(nickname_form(session, games[last_game_id]), id='nickname-area'), # Prompt for name if on leaderboard
                        A(Button("View game summary",  style=btn_style), href=f"/game-summary?game_id={last_game_id}",
                        style="border-bottom: 0px;"),
                        Form(Button("Play Again!",type="submit", style=btn_style), hx_post="/join",
                             hx_target="#active-area",hx_swap="outerHTML"),
                        style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;"
                    ),
                id="active-area")
    
    # If they're not in an active game or the queue, show the start game button
    intro = P("Welcome to Moodle!",
              "Put your drawing skills to the test while a team of AI models try to guess your word.",
              style="max-width: 600px; margin: 0 auto; text-align: center;")
    return Div(Br(), intro, Br(), # <<< TODO restyle this
                P("Are you ready?"),
                Form(Button("Play Game!",type="submit"), hx_post="/join",
                    hx_target="#active-area",hx_swap="outerHTML"),
                id="active-area")

@app.get('/guesses')
def get_recent_guesses(session):
    global recent_guesses
    # print("Getting recent guesses")
    # print(recent_guesses)
    if not active_games or session['sid'] not in [game.player for game in active_games]:
        return ""
    game = [game for game in active_games if game.player == session['sid']][0]
    outstanding_guesses = [guess for guess in recent_guesses if guess['game'] == game.id]
    recent_guesses = [guess for guess in recent_guesses if guess['game'] != game.id]
    if not outstanding_guesses:
        return ""

    gs = []
    game_ended = False
    for guess in outstanding_guesses:
        gs.append(Div(
            P(f"{guess['guesser']}: {guess['guess']}" + (f" (correct!)" if guess['correct'] else ""),
            style="margin-bottom: 0.5rem;"),
            cls="guess"
        ))
        if guess['correct']:
            game_ended = True
    if game_ended:
        # Could make this a script that uses htmx.ajax in a Timeout instead of using a hidden div
        gs.append(Hidden("endgame", hx_get=f"/active_area?last_game_id={game.id}", hx_target="#active-area", 
                         hx_trigger="load delay:3s",hx_swap="outerHTML", id="endgame", hx_swap_oob="outerHTML"))
        _ = end_game(game)
    return *gs, ""

# JS: Countdown timer that navigates to /end-game when time is up
def countdown(start_time):
  elapsed_time = time.time() - start_time
  time_left = game_max_duration - elapsed_time
  return Div(
        Div(
            Div(id='progress'),
            id='progress-bar'
        ),
        P('Time left: -- seconds', id='time-left', hidden=True),
        Hidden(start_time, id="start-time"),
        Hidden(game_max_duration, id="game-max-duration"),
        # See script for countdown timer javascript
        id="countdown-container", cls="actitem countdown")

# Ends game (if one running for this player) and redirects to summary
@app.get("/endgame")
def end(session):
    # Check if there's an active game
    if not active_games or not session['sid'] in [game.player for game in active_games]:
        return P("No active games. Return ", A("home", href="/", style="color: black;"))

    # End the game
    game = [game for game in active_games if game.player == session['sid']][0]
    end_game(game)
    
    # Replace active area
    return active_area(session, last_game_id=game.id)

# Make a GIF of a game
def create_game_gif(game):
    game_images = drawings(where=f'game={game.id}')
    game_guesses = guesses(where=f'game={game.id}')
    frames = []
    for i, img in enumerate(game_images):
        frame = PILImage.new('RGB', (840, 512), color='white')
        game_img = PILImage.open(img.fn).resize((512, 512))
        frame.paste(game_img, (0, 0))
        draw = ImageDraw.Draw(frame)
        font = ImageFont.truetype(
            "font.ttf", 20)
        y_offset = 10
        has_guesses = False
        for guess in game_guesses:
            if guess.drawing_fn == img.fn:
                text = f"{guess.guesser}: {guess.guess}"
                draw.text((532, y_offset), text, font=font, fill='black')
                y_offset += 30
                has_guesses = True
        if has_guesses:
            frames.append(frame)
        if i == len(game_images) - 1:
            text = "Word was: " + games[game.id].word
            draw.text((532, y_offset), text, font=font, fill='black')
            frames.append(frame)

    # Save the frames as a GIF
    if not frames: return None
    if len(frames) <= 1: return None
    gif_path = f"data/images/game_{game.id}.gif"
    frames[0].save(gif_path,save_all=True,append_images=frames[1:],
                   duration=1000,loop=0)

    return gif_path

@threaded # Runs in a separate temporary thread
def end_game(game):
    # End the game
    with db_lock:
        game.end_time = time.time()
        game.approved = False
        games.update(game)
    active_games.remove(game)
    # Save GIF
    gif_path = create_game_gif(game)
    with db_lock:
        game.game_gif = gif_path
        games.update(game)
    # TODO use model to see if it's a troll or legit.
    if True:
        final_draw = drawings[game.last_drawing]
        image_fn = final_draw.fn
        game.approved = True
        with db_lock:
            games.update(game)

# Get the image from a canvas and process it
@app.post("/process-canvas")
def process_canvas(image: str, session):
    if not active_games or session['sid'] not in [game.player for game in active_games]:
        return {"active_game": "no"}
    game = [game for game in active_games if game.player == session['sid']][0]
    image_bytes = image.file.read() # TODO async
    fn = f"data/images/{uuid.uuid4()}.png"
    with open(fn, 'wb') as f:
        f.write(image_bytes)
    with db_lock:
        drawing = drawings.insert(Drawing(fn=fn, game=game.id, time=time.time()))
        game.last_drawing = drawing.id
        games.update(game)
    return {'active_game': 'yes', 'latest_image': fn}
    
# They clicked "Play A Game!" to start a game - updates active area
@app.post("/join")
def join(session):

  print("Starting game for", session)

  # If games are all full, add to queue (or update last request time if already in queue)
  if len(active_games) >= max_concurrent_games:
    if session['sid'] not in player_queue:
      player_queue[session['sid']] = {'last_request': time.time()}

  # There are free games
  else:
    # If there's a queue, start a game with the first player in the queue
    if player_queue:
        player_id, _ = player_queue.popitem(last=False)
        start_game(player_id)
    # Otherwise, start a game with the current player
    start_game(session['sid'])

  return active_area(session)

@app.get('/leaderboard')
def leaderboard():
    # TODO top 5 of the day maybe?
  fastest_games = games(where="end_time IS NOT NULL",
                        order_by="(end_time - start_time) ASC",
                        limit=10)
  rows = []
  for i, game in enumerate(fastest_games, 1):
    duration = game.end_time - game.start_time
    player_name = game.player_name if game.player_name else "Anonymous"
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
      H1("Top 10 Fastest Games:", style="text-align: left;"),
      table,
      A("Back to Home", href="/"),
      cls='container')

def nickname_form(session, game):
    is_player = session['sid'] == game.player
    nickname_form = ""
    if is_player and not game.player_name:
        if 'nickname' in session:
            with db_lock:
                game.player_name = session['nickname']
                games.update(game)
        else: # need a nickname from them
            top_10 = games(where="end_time IS NOT NULL", order_by="(end_time - start_time) ASC", limit=10)
            if game in top_10:
                nickname_form = Div(
                    P("You're in the top 10! Set a nickname for the leaderboard:"),
                    Form(Input(type="text",name="nickname", placeholder="Enter your nickname"),
                            Input(type="submit", value="Save Nickname"),
                            hx_post=f"/save-nickname/{game.id}",
                            hx_target="#nickname-area"),
                )
    return nickname_form

@app.get('/game-summary')
def game_summary_page(game_id: int, session):
    game = games[game_id]
    is_player = session['sid'] == game.player
    gif = Img(src=f"/{game.game_gif}", width=840, height=512) if game.game_gif else ""
    gs = [Li(f"{guess.guesser} guessed: {guess.guess}" + (" (correct!)" if guess.guess == game.word else "")) for guess in guesses(where=f'game={game_id}')]
    # Create Twitter share button if the player is viewing their own game
    twitter_share = ""
    if session['sid'] == game.player:
        share_text = f"I just drew '{game.word}' in {game.end_time - game.start_time:.2f} seconds on Moodle! Can you beat my time?"
        share_url = domain + f"/game-summary?game_id={game_id}"
        twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
        twitter_share = Div(
            P("Show off your prowess on X/Twitter:"),
            A(Button("Share Game"),
                        href=twitter_url,
                        target="_blank",
                        cls="btn btn-primary twitter-s`hare-button"),
            P(""),)

    # If this is a top 10 game and they don't have a nickname, prompt them to set one
    
    
        
    content = [
        H3(f"Game {game_id} Summary"),
        P(f"Word: {game.word}"),
        P(f"Game duration: {game.end_time - game.start_time:.2f} seconds") if game.end_time else P("Game still active."),
        Div(
            P(f"Player: {game.player_name}") if game.player_name else "",
            nickname_form(session, game),
            id="nickname-area"),
        twitter_share,
        gif
    ]
    
    # Twitter meta tags
    metas = [
        Meta(name="twitter:card", content="summary_large_image"),
        Meta(name="twitter:site", content="@johnowhitaker"),
        Meta(name="twitter:title", content=f"Game {game_id} Summary"),
        Meta(name="twitter:description", content=f"Word: {game.word}"),
        Meta(name="twitter:image", content=f"{domain}/{game.game_gif}" if game.game_gif else f"{domain}/{game.last_drawing}"),
    ]

    return Title("Moodle Game Summary"), *metas, Navbar("leaderboard"),  Main(
      *content,
      cls='container')

    # return Html(
    #     Head(confetti, sakura, js, css, mod, *metas, Title(f"Game {game_id} Summary")),
    #     Body(Navbar("summary"), *content, cls='container'))

# In the summary page, you can set a nickname for the leaderbaord
@app.post("/save-nickname/{game_id}")
def save_nickname(game_id: int, nickname: str, session):
  game = games[game_id]
  if session['sid'] == game.player:
    game.player_name = nickname
    games.update(game)
    session['nickname'] = nickname
    return P(f"Player: {game.player_name}")
  else:
    return P("You are not authorized to set a nickname for this game.")

@app.get("/past-games-area")
def past_games_area(page:int=1):
   # Infinite scroll sort of deal
    games_list = games(where="end_time IS NOT NULL", order_by="end_time DESC", limit=10, offset=(page-1)*10)
    content = Div(*[Img(src=f"/{game.game_gif}", alt=f"game {game.id}") for game in games_list if game.game_gif], id="past-games")
    new_btn = Button("Load More", hx_get=f"/past-games-area?page={page+1}", hx_target="#past-games-area", hx_swap="beforeend",
                     id="load-more", hx_swap_oob="outerHTML"),
    return content, new_btn

@app.get('/gallery')
def spectate():
    content, new_btn = past_games_area()
    return Title("Moodle - Recent Games"), Body(
        Navbar(page='spectate'),
        Div(
            H1('Gallery'),
            P("Some recent games:"),
            Div(content, id="past-games-area"),
            new_btn,
            cls='content'
        )
    )

@app.get('/stats')
def stats():
  return Title("AI Pictionary"), Body(
      Navbar(page='stats'),
      Div(
        H1('Stats'),
        P("Coming soon: stats on which models play best!"),
        cls='content'
      )
    )

about_md = """## About
          
Moodle was born from a demo that got a little out of control. I wanted to see if any of these multi-modal
LLMs could play pictionary. It turns out they can! And it's rather fun...

### Technical Details
          
This app is built with a new framework we're working on - [FastHTML](https://fastht.ml). It's a Python framework 
that makes it easy to build web apps with Python and HTML. It's still in development, but it's already pretty powerful!
          
The canvas (HTML/JS) sends images to the backend, which ships them off to a few different models that try to guess the word.
          
### Future Plans
          
I think this will be a fun, quirky eval for models. I'm saving all the drawings (I hope you don't draw anything bad) and the progressions
will make a good classification problem. Can a model guess from the final image? from the sequence? etc..."""

@app.get('/about')
def about():
  return Title("About"), Navbar("about"), Body(
      Div(about_md, cls='marked', style='text-align: left;'),
      A("Back to Home", href="/"),
      cls='content')


# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
  return FileResponse(f'{fname}.{ext}')


# Threaded guess loop #
# For each game, for each model, we have a thread going that 
# sends the image to the model and gets the guess back

## API clients ##
import google.generativeai as genai
from openai import AzureOpenAI
import anthropic

genai.configure(api_key=os.environ.get("G_API_KEY"))
openai_client = AzureOpenAI(
  azure_endpoint='https://answeroai-eus2.openai.azure.com',
  api_key=os.environ.get("AZURE_KEY"),
  api_version="2024-02-01",
)
anthropic_client = anthropic.Anthropic(
  api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

## Guess functions ##
def make_prompt(guess_history=None):
    prompt = "Guess the pictionary prompt. Reply with a single word only."
    if guess_history:
        prompt += f"\nPast guesses: {', '.join([g['guess'] for g in guess_history])}"
    return prompt

def guess_gemini(image_fn, guess_history=None):
    img = PILImage.open(image_fn)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([make_prompt(guess_history), img])
    response.resolve()
    return "Flash 1.5", response.text

def guess_gpt_4o(image_fn, guess_history=None):
    base64_image = base64.b64encode(open(image_fn, 'rb').read()).decode('utf-8')
    completion = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role":
        "user",
        "content": [{
            "type": "text",
            "text": make_prompt(guess_history)
        }, {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }]
    }])
    return "GPT-4o", completion.choices[0].message.content

def guess_haiku(image_fn, guess_history=None):
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
              "text": make_prompt(guess_history),
          }],
      }],
  )
  caption = message.content[0].text
  return "Haiku", caption

def random_guess(image_fn, guess_history=None):
  if guess_history:
    all_guesses = [g['guess'] for g in guess_history]
    print("(random) all past guesses:)", all_guesses)
  return 'Random', random.choice(words)

# There's also a thread prunes players from the queue if they've not checked in for a while
def queue_pruner():
    global player_queue
    for player_id in list(player_queue.keys()):
        if time.time() - player_queue[player_id]['last_request'] > 60: # TODO lower this time
            del player_queue[player_id]
            print(f"Removed {player_id} from queue.")

# And one that ends games after a certain time
def game_ender():
    for game in active_games:
        if time.time() - game.start_time > game_max_duration + 1:
            end_game(game)
            print(f"Ended game {game.id}.")
            break

# guessers = {"random": random_guess, 'random2':random_guess} # for debugging
guessers = {"gemini": guess_gemini, "gpt-4o": guess_gpt_4o, "haiku": guess_haiku}
class BackgroundTask(threading.Thread):
    def __init__(self, task_name, stop_event, func, game_idx=None, interval=3):
        threading.Thread.__init__(self)
        self.task_name = task_name
        self.stop_event = stop_event
        self.func = func
        self.game_idx = game_idx
        self.interval = interval
    def run(self):
        # Debug info
        if self.game_idx is None: 
            if thread_debug: print(f"Task {self.task_name} is starting with func {self.func}")
        else: 
            if thread_debug: print(f"Task {self.task_name} is starting for game {self.game_idx} with guesser {self.func}")
        
        # Run in loop
        while not self.stop_event.is_set():
            start_time = time.time()
            if thread_debug: print(f"Task {self.task_name} is running")
            if self.game_idx is None:
                self.func()
            else:
                # Threads do nothing if there are not enough active games
                if self.game_idx >= len(active_games):
                    time.sleep(1)
                    continue
                # Get game info
                game = active_games[self.game_idx]
                image_fn  = ""
                if game.last_drawing:
                    with db_lock:
                        drawing = drawings[game.last_drawing]
                        image_fn = drawing.fn
                guess_history = guesses(where=f"game == {game.id}")
                guess_history = [{'guesser': g.guesser, 'guess': g.guess} for g in guess_history]
                word = game.word
                game_id = game.id
                try:
                    if thread_debug: print(f"Game idx {self.game_idx} is running for game {game_id} with word {word}, image {image_fn}")
                    guess = self.func(image_fn, guess_history)
                    guesser_name, guess_text = guess
                    guess_text = guess_text.strip().lower()
                    guess_text = ''.join(e for e in guess_text if e.isalnum() or e.isspace())
                    is_correct = guess_text == word
                    recent_guesses.append({'guesser': guesser_name, 'guess': guess_text, 'correct': is_correct,'game': game_id})
                    with db_lock:
                        guesses.insert(Guess(drawing_fn=image_fn, game=game_id, guess=guess_text,
                                             guesser=guesser_name, word=word, correct=is_correct))
                    if thread_debug: print(f"Game idx {self.game_idx} guess by {guesser_name}: {guess_text} (correct: {is_correct})")
                except Exception as e:
                    print(f"Error: {e}")

            time.sleep(max(0, self.interval - (time.time() - start_time)))

        if thread_debug: print(f"Task {self.task_name} is stopping")
        return True

stop_event = threading.Event()
tasks = []

def start_background_tasks():
    global tasks
    if len(tasks) > 0:
        print("Tasks already running")
        return
    for i in range(max_concurrent_games):
        for guesser in guessers:
            task = BackgroundTask(f'game_{i}_guesser_{guesser}', stop_event, guessers[guesser], i)
            tasks.append(task)
    tasks.append(BackgroundTask('queue_pruner', stop_event, queue_pruner, interval=1))
    tasks.append(BackgroundTask('game_ender', stop_event, game_ender, interval=1))
    for task in tasks:
        task.start()
        # time.sleep(0.5) # Stagger the starts

def stop_background_tasks():
    print("Stopping all tasks...")
    stop_event.set()
    for task in tasks:
        task.join()
    print("All tasks stopped")

@app.on_event("startup")
async def startup_event():
    start_background_tasks()

@app.on_event("shutdown")
async def shutdown_event():
    stop_background_tasks()

if __name__ == "__main__":
    try:
        run_uv()
    except KeyboardInterrupt:
        pass
    finally:
        stop_background_tasks()
        sys.exit(0)