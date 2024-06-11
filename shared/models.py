import discord
from dataclasses import dataclass


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
