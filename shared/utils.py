import discord
import re
from datetime import datetime, timedelta, timezone
from shared.models import MessageWithReactionCount
from schemas.user import User


async def get_channel_messages_past_24_hours(channel: discord.TextChannel) -> list[discord.Message]:
    current_datetime_utc = datetime.now(timezone.utc)
    last_21pm_utc = (current_datetime_utc - timedelta(hours=24)
                     ).replace(hour=21, minute=0, second=0, microsecond=0)
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


async def get_messages_with_attachments_and_reactions(messages: list[discord.Message]) -> list[MessageWithReactionCount]:
    valid_messages_with_reaction_count: list[MessageWithReactionCount] = []

    for message in messages:
        # choose messages with atleast 1 reaction and 1 attachment
        if len(message.attachments) > 0 and len(message.reactions) > 0:
            attachment = message.attachments[0]
            # validate attachment type
            if attachment.filename.lower().endswith(('.mp4', '.mov', '.wmv', '.avi', '.gif', '.webm', '.mkv')):
                unique_reactors_count = await get_unique_reactors_count(message)
                valid_messages_with_reaction_count.append(MessageWithReactionCount(
                    message=message, unique_reactions_count=unique_reactors_count))

    return valid_messages_with_reaction_count


def convert_user_to_markdown(user: User) -> str:

    return f"**Name:** {user.name}\n**Youtube:** {user.youtube or ''}\n**Twitter:** {user.twitter or ''}\n**Instagram:** {user.instagram or ''}\n**Website:** {user.website or ''}\n**Okay To Feature:** {user.featured}"
