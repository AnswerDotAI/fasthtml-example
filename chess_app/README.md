# Chess Example

Minimal example showing how to have a multiplayer chess game. Uses websockets to allow for real-time updates.

## Setup

Install the requirements using pip:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python chess_app.py
```

Open your browser to `http://localhost:5001` and you should see the chess board. Currently only piece movement is implemented, not piece capture or check/checkmate.