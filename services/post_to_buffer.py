import requests
import json
import os
from dotenv import load_dotenv
from shared.models import SocialMediaPost

load_dotenv()

url = os.getenv("ZAPIER_BUFFER_URL")


def post_to_buffer(social_media_post: SocialMediaPost) -> None:

    payload = json.dumps({
        "video_url": social_media_post.attachment_url,
        "video_title_youtube": social_media_post.video_title_youtube,
        "video_description_youtube": social_media_post.video_description_youtube,
        "video_caption_tiktok": social_media_post.video_caption_tiktok,
        "video_caption_instagram": social_media_post.video_caption_instagram
    })
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
