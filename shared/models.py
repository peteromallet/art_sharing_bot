import discord
from dataclasses import dataclass
from enum import Enum


@dataclass
class MessageWithReactionCount():
    message: discord.Message
    unique_reactions_count: int


@dataclass
class SocialMediaPost():
    post_id: int
    caption: str
    attachment_url: str
    attachment_name: str
    post_jump_url: str


class SocialMedia(Enum):
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
