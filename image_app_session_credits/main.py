from fastcore.parallel import threaded
from fasthtml.common import *
import uuid, os, uvicorn, requests, replicate, stripe
from PIL import Image
from starlette.responses import RedirectResponse

# Replicate setup (for generating images)
replicate_api_token = os.environ['REPLICATE_API_KEY']
client = replicate.Client(api_token=replicate_api_token)

# Stripe (for payments)
stripe.api_key = os.environ["STRIPE_KEY"]
webhook_secret = os.environ['STRIPE_WEBHOOK_SECRET']
DOMAIN = os.environ['DOMAIN']

# Global balance (NB: resets every restart)
global_balance = 100

# gens database for storing generated image details
tables = database('data/gens.db').t
gens = tables.gens
if not gens in tables:
    gens.create(prompt=str, session_id=str, id=int, folder=str, pk='id')
Generation = gens.dataclass()


# Flexbox CSS (http://flexboxgrid.com/)
gridlink = Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css", type="text/css")

# Our FastHTML app
app = FastHTML(hdrs=(picolink, gridlink))

# Main page
@app.get("/")
def home(session):
    if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
    inp = Input(id="new-prompt", name="prompt", placeholder="Enter a prompt")
    add = Form(Group(inp, Button("Generate")), hx_post="/", target_id='gen-list', hx_swap="afterbegin")
    gen_containers = [generation_preview(g, session) for g in gens(limit=10, where=f"session_id == '{session['session_id']}'")]
    gen_list = Div(*gen_containers[::-1], id='gen-list', cls="row") # flexbox container: class = row
    return Title('Image Generation Demo'), Main(
        H1('Image Generation Demo (Sessions, Credits)'),
        P("Hello", str(session)),
        get_balance(),  # Live-updating balance
        P(A("Buy 50 more", href="/buy_global"), " to share ($1)"),
        add, gen_list, cls='container')

# Show the image (if available) and prompt for a generation
def generation_preview(g, session):
  if 'session_id' not in session: return "No session ID"
  if g.session_id != session['session_id']: return "Wrong session ID!"
  grid_cls = "box col-xs-12 col-sm-6 col-md-4 col-lg-3"
  image_path = f"{g.folder}/{g.id}.png"
  if os.path.exists(image_path):
    return Div(Card(
        Img(src=image_path, alt="Card image", cls="card-img-top"),
        Div(P(B("Prompt: "), g.prompt, cls="card-text"), cls="card-body"),
    ),
               id=f'gen-{g.id}',
               cls=grid_cls)
  return Div(f"Generating with prompt '{g.prompt}'...",
             id=f'gen-{g.id}',
             hx_get=f"/gens/{g.id}",
             hx_trigger="every 2s",
             hx_swap="outerHTML",
             cls=grid_cls)

# A pending preview keeps polling this route until we return the image preview
@app.get("/gens/{id}")
def preview(id:int, session):
    return generation_preview(gens.get(id), session)

# Likewise we poll to keep the balance updated
@app.get("/balance")
def get_balance():
  return Div(P(f"Global balance: {global_balance} credits"),
             id='balance', hx_get="/balance",
             hx_trigger="every 2s", hx_swap="outerHTML")

# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')

# Generation route
@app.post("/")
def post(prompt: str, session):

    # Check for session ID
    if 'session_id' not in session: return "No session ID"

    clear_input = Input(id="new-prompt",
                        name="prompt",
                        placeholder="Enter a prompt",
                        hx_swap_oob='true')

    global global_balance

    # Warn if we're out of balance
    if global_balance < 1: return Div(P("Out of balance!")), clear_input

    # Decrement balance
    global_balance -= 1

    # Generate as before
    folder = f"data/gens/{str(uuid.uuid4())}"
    os.makedirs(folder, exist_ok=True)
    g = gens.insert(
        Generation(prompt=prompt,
                    folder=folder,
                    session_id=session['session_id']))
    generate_and_save(g.prompt, g.id, g.folder)

    return generation_preview(g, session), clear_input

# Generate an image and save it to the folder (in a separate thread)
@threaded
def generate_and_save(prompt, id, folder):
    output = client.run(
        "playgroundai/playground-v2.5-1024px-aesthetic:a45f82a1382bed5c7aeb861dac7c7d191b0fdf74d8d57c4a0e6ed7d4d0bf7d24",
        input={
            "width": 1024,"height": 1024,"prompt": prompt,"scheduler": "DPMSolver++",
            "num_outputs": 1,"guidance_scale": 3,"apply_watermark": True,
            "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
            "prompt_strength": 0.8, "num_inference_steps": 25
        }
    )
    Image.open(requests.get(output[0], stream=True).raw).save(f"{folder}/{id}.png")
    return True

# Stripe
# We send the user here to buy credits
@app.get("/buy_global")
def buy_credits(session):
  if not 'session_id' in session:
    return "Error no session id"
  # Create Stripe Checkout Session
  s = stripe.checkout.Session.create(
      payment_method_types=['card'],
      line_items=[{
          'price_data': {
              'currency': 'usd',
              'unit_amount': 100,
              'product_data': {
                  'name': 'Buy 50 credits for $1 (to share)',
              },
          },
          'quantity': 1,
      }],
      mode='payment',
      success_url=DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url=DOMAIN + '/cancel',
  )

  # Send the USER to STRIPE
  return RedirectResponse(s['url'])


# STRIPE sends the USER here after a payment was canceled.
@app.get("/cancel")
def cancel():
  return P(f'Cancelled.', A('Return Home', href='/'))


# STRIPE sends the USER here after a payment was 'successful'.
@app.get("/success")
def success():
  return P(f'Success!', A('Return Home', href='/'))


# STRIPE calls this to tell APP when a payment was completed.
@app.post('/webhook')
async def stripe_webhook(request):
  global global_balance
  print(request)
  print('Received webhook')
  payload = await request.body()
  payload = payload.decode("utf-8")
  signature = request.headers.get('stripe-signature')
  print(payload)

  # Verify the Stripe webhook signature
  try:
    event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
  except ValueError:
    print('Invalid payload')
    return {'error': 'Invalid payload'}, 400
  except stripe.error.SignatureVerificationError:
    print('Invalid signature')
    return {'error': 'Invalid signature'}, 400

  # Handle the event
  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']
    print("Session completed", session)
    global_balance += 50
    return {'status': 'success'}, 200

if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', port=int(os.getenv("PORT", default=5000)))
