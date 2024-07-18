# Chatbot Demo

TODO intro

- `basic.py`: A minimal version of the app, showing the chat bubble styling as described in [this tutorial](https://fhdocs.answer.ai/by_example.html#full-example-3---chatbot-example-with-daisyui-components).
- `polling.py`: Extending the basic chatbot with a polling mechanism so that the UI updates as soon as the user sends a message, and then streams the response from the chat model.
- `websockets.py`: Extending the basic chatbot to use websockets.

## Basic Funtionality

blablabla

## Polling

blablabla

## Websockets

We keep track of open connections.

We return a blank message straight away, then send the response when it's ready (to any open connections). This is not a multi-user app!

For streaming, we can replace the message as chunks come in, but to make it possible to copy text as it streams in we instead append to the message.

## Multi-user