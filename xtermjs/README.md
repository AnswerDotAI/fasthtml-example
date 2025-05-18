# XTermJS Terminal Example

This example demonstrates how to create a web-based terminal using FastHTML and XTermJS.

## Overview

This application creates a browser-based terminal that connects to a real shell on the server. It uses:

- **FastHTML** for the web application framework
- **XTermJS** for the terminal interface
- **WebSockets** for bidirectional communication
- **PTY** (pseudo-terminal) for shell interaction

## How to Run

1. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5001
   ```

## Code Explanation

The implementation consists of two main files:

- `main.py`: The server-side Python application that creates the PTY and handles WebSocket communication
- `static/terminal.js`: The client-side JavaScript that initializes XTermJS and manages the WebSocket connection

## Learn More

To learn more about FastHTML, check out the [FastHTML documentation](https://github.com/AnswerDotAI/fasthtml).