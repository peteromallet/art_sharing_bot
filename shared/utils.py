import discord
import re
from datetime import datetime, timedelta, timezone
from shared.models import MessageWithReactionCount, SocialMedia
from schemas.user import User
import aiohttp
import subprocess


async def get_channel_messages_past_24_hours(channel: discord.TextChannel) -> list[discord.Message]:
    current_datetime_utc = datetime.now(timezone.utc)
    last_21pm_utc = (current_datetime_utc - timedelta(hours=24)
                     ).replace(hour=19, minute=0, second=0, microsecond=0)  # TODO: set this to 9pm utc later
    messages = [message async for message in channel.history(after=last_21pm_utc, limit=None)]
    return messages


async def get_unique_reactors_count(message: discord.Message) -> int:
    unique_user_ids = set()

    for reaction in message.reactions:
        async for user in reaction.users():
            unique_user_ids.add(user.id)

    return len(unique_user_ids)


def replace_user_mentions_with_usernames(message: discord.Message) -> str:
    msg = message.content
    mentions_str = re.findall(r'<@\d+>', msg)

    for mention_str in mentions_str:
        mention = [
            m for m in message.mentions if mention_str == f"<@{m.id}>"][0]
        msg = msg.replace(mention_str, f"@{mention.global_name}")
    return msg


def ensure_blockquote_in_all_lines(text: str) -> str:
    if text == '':
        return text
    new_lines = (text.split('\n'))
    new_lines = list(map(lambda x: f"\n> _{x}_", new_lines))
    return ''.join(new_lines)


def get_messages_with_most_reactions(messages_with_reaction_counts: list[MessageWithReactionCount], top_n: int) -> list[MessageWithReactionCount]:
    # Get the top n highest reaction counts
    top_n_reaction_counts = [msg.unique_reactions_count for msg in sorted(
        messages_with_reaction_counts, key=lambda x: x.unique_reactions_count, reverse=True)][:top_n]

    # filter out messages with unique_reactions_count not in top_n_reaction_counts
    top_messages = [
        msg for msg in messages_with_reaction_counts if msg.unique_reactions_count in top_n_reaction_counts]
    top_messages = sorted(
        top_messages, key=lambda x: x.unique_reactions_count, reverse=True)
    return top_messages


async def get_messages_with_attachments_and_reactions(messages: list[discord.Message], min_reaction_count: int = 1) -> list[MessageWithReactionCount]:
    valid_messages_with_reaction_count: list[MessageWithReactionCount] = []

    for message in messages:
        # choose messages with atleast 1 reaction and 1 attachment
        if len(message.attachments) > 0 and len(message.reactions) > 0:
            attachment = message.attachments[0]
            # validate attachment type
            if attachment.filename.lower().endswith(('.mp4', '.mov', '.wmv', '.avi', '.gif', '.webm', '.mkv')):
                unique_reactors_count = await get_unique_reactors_count(message)

                # Ensure the number of unique reactors is greater than threshold
                if unique_reactors_count >= min_reaction_count:
                    valid_messages_with_reaction_count.append(MessageWithReactionCount(
                        message=message, unique_reactions_count=unique_reactors_count))

    return valid_messages_with_reaction_count


def convert_user_to_markdown(user: User) -> str:

    return f"**Name:** {user.name}\n**Youtube handle:** {user.youtube or ''}\n**Twitter handle:** {user.twitter or ''}\n**Instagram handle:** {user.instagram or ''}\n**Tiktok handle:** {user.tiktok or ''}\n**Website:** {user.website or ''}\n**DM Notifications:** {user.dm_notifications}\n**Okay To Feature:** {user.featured}"


async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await resp.read())


def truncate_with_ellipsis(text, max_length):
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length-3] + "..."


def create_post_caption(user_details: User, comment: str, platform: SocialMedia) -> str:
    caption = "Featured piece by"
    if platform == SocialMedia.TWITTER:
        if user_details.twitter is not None:
            user_twitter = user_details.twitter
            if user_twitter.startswith('http'):
                caption += f" {user_twitter}"
            else:
                caption += f" {'@' if user_twitter[0] != '@' else ''}{user_twitter}"
        else:
            caption += f" {user_details.name}"

        if comment and len(comment) > 0:
            # max length of twitter caption is 280, must accommodate for 3 lines of text
            caption += f"\n\nArtist Comment: \"{truncate_with_ellipsis(comment, 200)}\""

    if platform == SocialMedia.INSTAGRAM:
        if user_details.instagram is not None:
            user_instagram = user_details.instagram
            if user_instagram.startswith('http'):
                caption += f" {user_instagram}"
            else:
                caption += f" {'@' if user_instagram[0] != '@' else ''}{user_instagram}"
        else:
            caption += f" {user_details.name}"

        if comment and len(comment) > 0:
            # max length of instagram caption is 2200
            caption += f"\n\nArtist Comment: \"{truncate_with_ellipsis(comment, 2000)}\""

    if platform == SocialMedia.TIKTOK:
        if user_details.tiktok is not None:
            user_tiktok = user_details.tiktok
            if user_tiktok.startswith('http'):
                caption += f" {user_tiktok}"
            else:
                caption += f" {'@' if user_tiktok[0] != '@' else ''}{user_tiktok}"
        else:
            caption += f" {user_details.name}"

        if comment and len(comment) > 0:
            # max length of tiktok caption is 2200 (not sure)
            caption += f"\n\nArtist Comment: \"{truncate_with_ellipsis(comment, 2000)}\""

    if platform == SocialMedia.YOUTUBE:
        if user_details.youtube is not None:
            user_youtube = user_details.youtube
            if user_youtube.startswith('http'):
                caption += f" {user_youtube}"
            else:
                caption += f" {'@' if user_youtube[0] != '@' else ''}{user_youtube}"
        else:
            caption += f" {user_details.name}"

        if comment and len(comment) > 0:
            # max length of youtube description is 5000
            caption += f"\n\nArtist Comment: \"{truncate_with_ellipsis(comment, 4800)}\""

    if user_details.website is not None:
        caption += f"\n\nYou can find their website here: {user_details.website}"

    return caption


def convert_gif_to_mp4(gif_local_path: str, mp4_save_path: str) -> None:
    subprocess.run(
        f"ffmpeg -loglevel error -y -i {gif_local_path} -c:v libx264 -preset slow -crf 18 {mp4_save_path}", shell=True)
