import os
from huggingface_hub import HfApi
from dotenv import load_dotenv
import time

load_dotenv()


def upload_video_to_huggingface(video_path: str) -> str:
    hf_api = HfApi(token=os.getenv("HUGGINGFACE_TOKEN"))

    repo_id = "xxxx/art-bot"
    video_id = int(time.time() * 1000)

    hf_api.upload_file(
        path_or_fileobj=video_path,
        path_in_repo=f"videos/{video_id}.mp4",
        repo_id=repo_id,
        repo_type="model"
    )

    return f"https://huggingface.co/{repo_id}/resolve/main/videos/{video_id}.mp4"
