# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-fasthtml>=0.4.5",
#     "othello",
# ]
#
# [tool.uv.sources]
# othello = { git = "https://github.com/phihung/othello.git" }
# ///
import asyncio
import time
from uuid import uuid1
from fasthtml.common import *
from othello import Game, AlphaBetaBot


app, rt = fast_app(
    hdrs=[Script(src="https://cdn.tailwindcss.com")],
    pico=False,
    ws_hdr=True,
)

games = {}
bot = AlphaBetaBot(7, 15)


@rt("/")
def get(uuid: str = None):
    if not uuid:
        uuid = str(uuid1())

    if uuid not in games:
        games[uuid] = Game.default()

    return cookie("uuid", uuid), make_app(uuid)


@app.get("/new")
def new(uuid: str = None):
    if uuid is not None and uuid in games:
        del games[uuid]
    return RedirectResponse("/")


def make_app(uuid):
    state = games[uuid].state
    return Div(
        Div(
            make_status_bar(state),
            Div(
                *(
                    Div(
                        make_stone(state.cells[i], i, uuid),
                        cls="size-12 xl:size-16 border border-sky-100",
                    )
                    for i in range(64)
                ),
                cls="grid grid-cols-8 gap-0 bg-green-300 mb-5 lg:mt-5",
                hx_ext="ws",
                ws_connect="/wscon",
            ),
            A("New Game", href="/new", cls="rounded-md bg-teal-600 mt-5 px-5 py-2"),
            cls="m-auto w-fit",
        ),
        cls="m-auto max-w-2xl bg-gray-200 lg:pt-12 pb-12 lg:mt-12",
    )


def make_stone(v, pos, uuid, highlight=False):
    style = "m-2 size-8 lg:size-12 rounded-full"
    if highlight:
        style += " border-indigo-500 border-2"
    stone = {}
    if v == "?":
        stone = dict(
            hx_trigger="click",
            hx_vals=f'{{"pos": {pos}, "uuid": "{uuid}"}}',
            ws_send=True,
            cls=f"{style} cursor-pointer bg-purple-200 hover:bg-purple-300",
        )
    elif v == "B":
        stone = dict(cls=f"{style} shadow-sm bg-black shadow-white")
    elif v == "W":
        stone = dict(cls=f"{style} shadow-sm bg-white shadow-black")
    return Div(**stone, id=f"cell-{pos}", hx_swap_oob="true")


def make_status_bar(state):
    status = get_status(state)
    return Div(
        Div(
            f"Black: {state.black_score}",
            cls="bg-black text-white w-32 h-12 text-center content-center",
        ),
        Div(status, cls="content-center"),
        Div(
            f"White: {state.white_score}",
            cls="bg-white text-black w-32 h-12 text-center content-center",
        ),
        cls="flex justify-between",
        id="status-bar",
        hx_swap_oob="true",
    )


def get_status(state):
    status = "Black turn"
    if state.ended:
        if state.white_score > state.black_score:
            status = "White won!"
        elif state.white_score < state.black_score:
            status = "Black won!"
        else:
            status = "Game draw!"
    elif state.player == "W":
        status = "White turn"
    return status


@app.ws("/wscon")
async def ws(uuid: str, pos: int, send):
    game = games[uuid]

    async def play(pos: int):
        prev_state = game.state
        state = game.make_move(pos) if pos >= 0 else game.pass_move()

        await send(make_stone(state.cells[pos], pos, uuid, highlight=True))

        for i, (c1, c2) in enumerate(zip(prev_state.cells, state.cells)):
            if i != pos and c1 != c2 or i == prev_state.last_move:
                await send(make_stone(c2, i, uuid))
        await send(make_status_bar(state))
        return state

    # Human
    state = await play(pos)
    if state.ended:
        return

    # Bot
    while True:
        now = time.time()
        pos = bot.find_move(game) if state.can_move else -1
        await asyncio.sleep(abs(1 - time.time() + now))
        state = await play(pos)
        if not state.can_move and not state.ended:
            # Human has no move
            state = await play(-1)
            assert pos != -1 and state.can_move and not state.ended
        else:
            break


if __name__ == "__main__":
    serve()
