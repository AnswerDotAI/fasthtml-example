# Chess Example

Minimal example showing how to have a multiplayer chess game. Uses websockets to allow for real-time updates.

## Setup

Install the requirements using pip:

```bash
pip install -r requirements.txt
```
To use the code editor you need to have a fireworks API key in your .env file to have autocompletions work.

Once you do, you can run the server:

```bash
python code_editor.py
```

Open your browser to `http://localhost:5001` and you should see the chess board. Currently only Javascript, Python, HTML, and CSS syntax highlighting is implemented. Completions are triggered on `.` and ` ` key down events. Saving the code is not implemented yet.