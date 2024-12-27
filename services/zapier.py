import requests
import json
import os
from dotenv import load_dotenv
from shared.models import SocialMediaPost

load_dotenv()

url_tiktok_buffer = os.getenv("ZAPIER_TIKTOK_BUFFER_URL")
url_instagram = os.getenv("ZAPIER_INSTAGRAM_URL")
url_youtube = os.getenv("ZAPIER_YOUTUBE_URL")


def post_to_tiktok_via_buffer(social_media_post: SocialMediaPost) -> None:

    payload = json.dumps({
        "video_url": social_media_post.attachment_url,
        "caption": social_media_post.video_caption_tiktok,
    })
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.request(
        "POST", url_tiktok_buffer, headers=headers, data=payload)


def post_to_youtube(social_media_post: SocialMediaPost) -> None:

    payload = json.dumps({
        "jump_url": social_media_post.post_jump_url,
        "video_url": social_media_post.attachment_url,
        "video_title_yt": social_media_post.video_title_youtube,
        "caption": social_media_post.video_description_youtube
    })
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.request(
        "POST", url_youtube, headers=headers, data=payload)


def post_to_instagram(social_media_post: SocialMediaPost) -> None:

    payload = json.dumps({
        "jump_url": social_media_post.post_jump_url,
        "video_url": social_media_post.attachment_url,
        "caption": social_media_post.video_caption_instagram
    })
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.request(
        "POST", url_instagram, headers=headers, data=payload)
