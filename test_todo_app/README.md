# Testing FastHTML Todo App

This project implements a few simple unit tests for [FastHTML Todo list application](https://github.com/AnswerDotAI/fasthtml-example/tree/main/01_todo_app) using Pytest and [FastHTML Client](https://docs.fastht.ml/api/core.html#client).


When running in test mode, the app now relies on a in-memory instance of Sqlite to make sure data is reset on every run. Test client and database table instance are defined as Pytest fixtures in `tests/conftest.py`.

## Running Locally

To run the app locally:

1. Clone the repository
2. Navigate to the project directory
3. Run `poetry install` to install dependencies
4. Run the following command: `poetry run python main.py`
5. To run tests, use `poetry run pytest tests`

