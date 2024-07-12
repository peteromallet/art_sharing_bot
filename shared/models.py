import discord
from dataclasses import dataclass
from enum import Enum
from schemas.user import User


@dataclass
class MessageWithReactionCount():
    message: discord.Message
    unique_reactions_count: int


@dataclass
class SocialMediaPost():
    post_id: int
    video_title_youtube: str
    video_description_youtube: str
    video_caption_tiktok: str
    video_caption_instagram: str
    caption_twitter: str
    attachment_url: str
    attachment_name: str
    post_jump_url: str
    local_path: str
    original_comment: str
    user_details: User


class SocialMedia(Enum):
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
