---
title: FastHTML Todos
colorFrom: green
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
---

# FastHTML on 🤗 Spaces

Deploy a FastHTML application to [HuggingFace Spaces](https://huggingface.co/spaces) for free with one command!

## Quickstart

1. Create a free account on [HuggingFace](https://huggingface.co)
2. Go to your account settings and create an access token with write access. Keep this token safe and don't share it.
3. Install the huggingface hub client library (`pip install huggingface-hub`).
5. Run the `depoy_hf.py` script and pass the name you want to give your space along with your token, e.g. `python deploy_hf.py fasthtml-todos <token>`.

By default this will upload a public space. You can make it private with the `--private` flag.

## Configuration

The space will upload a backup of your database to a [HuggingFace Dataset](https://huggingface.co/datasets). By default it will be private and its name will be `<your-huggingface-id>/todos-backup`. You can change this behavior in the `config.py` file.

If you so chose, you can disable the automatic backups and use [persistent storage](https://huggingface.co/docs/hub/en/spaces-storage#persistent-storage-specs) instead for $5/month (USD). 

