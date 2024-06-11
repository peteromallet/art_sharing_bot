import asyncio
from discord.ext import commands
from shared.models import MessageWithReactionCount
from shared.utils import replace_user_mentions_with_usernames, ensure_blockquote_in_all_lines, get_channel_messages_past_24_hours, get_messages_with_most_reactions, get_messages_with_attachments_and_reactions

from constants import ART_SHARING_CHANNEL, PROJECT_ART_SHARING_CHANNEL


async def handle_display_top_posts_interaction(bot: commands.Bot, top_n: int) -> None:

    # Get all messages from #art_sharing in the past 24 hours (9pm UTC yesterday to 9pm UTC today)
    art_sharing_channel = bot.get_channel(ART_SHARING_CHANNEL)
    messages = await get_channel_messages_past_24_hours(art_sharing_channel)

    valid_messages_with_attachments_and_reactions: list[MessageWithReactionCount] = await get_messages_with_attachments_and_reactions(messages)
    top_messages = get_messages_with_most_reactions(
        valid_messages_with_attachments_and_reactions, top_n=top_n)  # top N

    # post updates to project_art_sharing_channel
    project_art_sharing_channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    title_message = f"# Here are the top {len(top_messages)} most reacted posts from {art_sharing_channel.jump_url} for today."
    await project_art_sharing_channel.send(title_message)

    for idx in range(1, len(top_messages)+1):
        top_message = top_messages[idx-1]

        msg_1 = f"## {idx}) By {top_message.message.author.display_name} ({top_message.unique_reactions_count} reactions):"
        msg_1 = "‎\n" + msg_1 if idx > 1 else msg_1
        await project_art_sharing_channel.send(content=msg_1)

        top_message_content = replace_user_mentions_with_usernames(
            top_message.message)
        msg_2 = ensure_blockquote_in_all_lines(top_message_content)
        await project_art_sharing_channel.send(content=msg_2, suppress_embeds=True) if len(msg_2) > 0 else None

        msg_3 = f"{top_message.message.attachments[0].url}"
        await project_art_sharing_channel.send(content=msg_3)

        msg_4 = f"You can find + react to the original post: {top_message.message.jump_url}"
        await project_art_sharing_channel.send(content=msg_4)

        await asyncio.sleep(1)
