# FastHTML Text Annotation App

This project implements a simple text annotation application using FastHTML, showcasing dynamic updates, database integration, and a user-friendly interface for annotating text data.

![Text Annotation App Screenshot](https://gist.github.com/user-attachments/assets/f28aff8c-3a55-439d-b605-d68c0b82c1b3)

Contributed by: [@altryne](https://x.com/altryne)

## Features

- View and navigate through text samples
- Annotate texts as correct or incorrect
- Add notes to each text sample
- Real-time updates without page reloads
- SQLite database integration
- Automatic loading of dummy data

## Technology Stack

- [FastHTML](https://github.com/AnswerDotAI/fasthtml): A Python framework for building dynamic web applications
- HTMX: For seamless client-side updates without full page reloads
- SQLite: For persistent data storage
- DaisyUI and Tailwind CSS: For styling and UI components

## Implementation Highlights

### App Setup and Database Integration

The app is set up using FastHTML's `fast_app` function, which creates the application, routing, database connection, and data model in a single line:

```python
python
app, rt, texts_db, Item = fast_app('texts.db', hdrs=(tlink, dlink, picolink, MarkdownJS(), HighlightJS()), live=True, id=int, messages=list, feedback=bool, notes=str, pk='id', render=render)
```

### Dummy Data

The app comes with a dummy data file `dummy_data.jsonl` containing sample text data. This file is loaded automatically when the app starts. If you want to load your own data, you'll need to replace this file with a new one in the same format.

The dummy data file contains JSON lines (JSONL) with the following structure on each line:

```json
[{"role":"user","content":"User's message"},{"role":"assistant","content":"Assistant's response"}]
```

### Running the App

To run the app, execute the following command:

```
python app.py
```

Open your web browser and navigate to `http://localhost:8000` to access the app.

## Customization

To use your own data instead of the dummy data:

1. Create a JSONL file with your data, following the structure described above
2. Replace the `dummy_data.jsonl` file in the `data` directory with your file
3. Ensure your file is named `dummy_data.jsonl` or update the file path in `main.py`

