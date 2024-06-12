from huggingface_hub import snapshot_download, upload_folder, create_repo, repo_exists, whoami
import os
import shutil
from config import Config


def get_dataset_id():
    token = os.getenv("HF_TOKEN")
    dataset_id = Config.dataset_id
    if "/" not in Config.dataset_id and token is not None:
        dataset_id = f"{whoami(token)['name']}/{Config.dataset_id}"
    return dataset_id

def download():
    is_space = os.getenv("SPACE_ID")
    dataset_id = get_dataset_id()
    if is_space and repo_exists(dataset_id, repo_type="dataset", token=os.getenv("HF_TOKEN")):
        cache_path = snapshot_download(repo_id=dataset_id, repo_type='dataset',
                                    token=os.getenv("HF_TOKEN"))
        shutil.copytree(cache_path, Config.db_dir, dirs_exist_ok=True)


def upload():
    import datetime

    is_space = os.getenv("SPACE_ID")
    if is_space:
        dataset_id = get_dataset_id()
        create_repo(dataset_id, token=os.getenv("HF_TOKEN"),
                    private=True, repo_type='dataset', exist_ok=True)
        upload_folder(folder_path=Config.db_dir,
                    repo_id=dataset_id, repo_type='dataset',
                    commit_message=f"backup at {datetime.datetime.now()}",
                    token=os.getenv("HF_TOKEN"))
