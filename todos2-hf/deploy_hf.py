from huggingface_hub import create_repo, upload_folder, add_space_secret, whoami
import datetime
from pathlib import Path
import argparse


def main(space_id, private, token):
    url = create_repo(space_id, token=token, repo_type='space',
                      space_sdk="docker", private=private, exist_ok=True)
    upload_folder(folder_path=Path("."),
                repo_id=space_id, repo_type='space',
                ignore_patterns=['__pycache__/*', '.sesskey', 'deploy_hf.py', 'data/*'],
                commit_message=f"deploy at {datetime.datetime.now()}",
                token=token)
    add_space_secret(space_id, token=token, key="HF_TOKEN", value=token)
    print(f"Deployed space at {url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload current directory to Hugging Face Spaces")
    parser.add_argument("space_id", help="ID of the space to upload to", default="fasthtml-todos")
    parser.add_argument("token",
                        help="Hugging Face token for authentication.")
    parser.add_argument("--private", action="store_true", help="Make the repository private")
    args = parser.parse_args()
    if "/" not in args.space_id:
        username = whoami(args.token)['name']
        args.space_id = f"{username}/{args.space_id}"
    main(args.space_id, args.private or False, args.token)