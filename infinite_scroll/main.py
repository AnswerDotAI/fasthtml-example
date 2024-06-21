from fasthtml import FastHTML, picolink
from fasthtml.common import *
import random, uvicorn

app = FastHTML(hdrs=(picolink,))

def create_card(number):
    color = f"hsl({random.randint(0, 360)}, 70%, 80%)"
    return Div(
        H2(f"Card {number}", style="color: black;"),
        P(f"This is card number {number}", style="color: black;"),
        cls="card",
        style=f"background-color: {color}; margin: 10px; padding: 20px; border-radius: 8px;"
    )

@app.get("/")
def home():
    initial_cards = [create_card(i) for i in range(1, 21)]
    return Title("Infinite Scroll Demo"), Main(
        H1("Infinite Scroll Demo"),
        Div(*initial_cards, id="card-container"),
        Div(
            hx_get="/more-cards",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="#card-container"
        ),
        style="max-width: 800px; margin: 0 auto;"
    )

@app.get("/more-cards")
def more_cards(request):
    # Get the current count from the query parameters
    start = int(request.query_params.get("start", 21))
    end = start + 20
    
    new_cards = [create_card(i) for i in range(start, end)]
    
    return *new_cards, Div(
            hx_get=f"/more-cards?start={end}",
            hx_trigger="intersect once",
            hx_swap="afterend",
            hx_target="this"
        )

if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)