# %% auto 0
__all__ = ['css', 'gridlink', 'htmx_ws', 'app', 'rt', 'grid', 'player_queue', 'background_task_coroutine', 'running',
           'update_grid', 'Grid', 'Home', 'get', 'WS', 'background_task', 'put']

# %% game_of_life.ipynb 2
from fasthtml import *
from fastcore.xml import to_xml
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute

import asyncio

css = Style(
    '''
#grid { display: grid; grid-template-columns: repeat(20, 20px); grid-template-rows: repeat(20, 20px);gap: 1px; }
.cell { width: 20px; height: 20px; border: 1px solid black; }
.alive { background-color: green; }
.dead { background-color: white; }
    '''
)

# Flexbox CSS (http://flexboxgrid.com/)
gridlink = Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css", type="text/css")
htmx_ws = Script(src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js")

app = FastHTML(hdrs=(picolink, gridlink, css, htmx_ws))
rt = app.route

# %% game_of_life.ipynb 3
grid = [[0 for _ in range(20)] for _ in range(20)]

def update_grid(grid: list[list[int]]) -> list[list[int]]:
    new_grid = [[0 for _ in range(20)] for _ in range(20)]

    def count_neighbors(x, y):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        count = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                count += grid[nx][ny]
        return count

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            neighbors = count_neighbors(i, j)
            if grid[i][j] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[i][j] = 0
                else:
                    new_grid[i][j] = 1
            else:
                if neighbors == 3:
                    new_grid[i][j] = 1
    return new_grid

# %% game_of_life.ipynb 4
def Grid():
    cells = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            cell_class = 'alive' if cell else 'dead'
            cell = Div(cls=f'cell {cell_class}', hx_put='/update', hx_vals={'x': x, 'y': y}, hx_swap='none', hx_target='#gol', hx_trigger='click')
            cells.append(cell)
    
    return Div(*cells, id='grid')

# %% game_of_life.ipynb 5
def Home():
    gol = Div(Grid(), id='gol', cls='row center-xs')
    run_btn = Button('Run', id='run', cls='col-xs-2', hx_put='/run', hx_target='#gol', hx_swap='none')
    pause_btn = Button('Pause', id='pause', cls='col-xs-2', hx_put='/pause', hx_target='#gol', hx_swap='none')
    reset_btn = Button('Reset', id='reset', cls='col-xs-2', hx_put='/reset', hx_target='#gol', hx_swap='none')

    return (
        Title('Game of Life'), Main(
            gol, Div(
                run_btn, pause_btn, reset_btn, cls='row center-xs'
            ),
            hx_ext="ws", ws_connect="/gol"
        )
    )

# %% game_of_life.ipynb 7
@rt('/')
def get():
    return Home()

# %% game_of_life.ipynb 8
player_queue = []
class WS(WebSocketEndpoint):
    encoding = 'text'

    async def on_connect(self, websocket):
        global player_queue
        player_queue.append(websocket)
        await websocket.accept()

    async def on_disconnect(self, websocket, close_code):
        global player_queue
        player_queue.remove(websocket)

app.routes.append(WebSocketRoute('/gol', WS))

# %% game_of_life.ipynb 9
async def background_task():
    global grid, running, player_queue
    while True:
        if running and len(player_queue) > 0:
            grid = update_grid(grid)
            for player in player_queue:
                await player.send_text(to_xml(Grid()))
        await asyncio.sleep(1.0)

# Create a task for the background task
background_task_coroutine = asyncio.create_task(background_task())

# %% game_of_life.ipynb 10
@rt('/update')
async def put(x: int, y: int):
    global grid, player_queue
    grid[y][x] = 1 if grid[y][x] == 0 else 0
    for player in player_queue:
        await player.send_text(to_xml(Grid()))

# %% game_of_life.ipynb 11
running = False
@rt('/run')
async def put():
    global running, player_queue
    running = True
    for player in player_queue:
        await player.send_text(to_xml(Grid()))

# %% game_of_life.ipynb 12
@rt("/reset")
async def put():
    global grid, running, player_queue
    grid = [[0 for _ in range(20)] for _ in range(20)]
    running = False
    for player in player_queue:
        await player.send_text(to_xml(Grid()))

# %% game_of_life.ipynb 13
@rt('/pause')
async def put():
    global running, player_queue
    running = False
    for player in player_queue:
        await player.send_text(to_xml(Grid()))
