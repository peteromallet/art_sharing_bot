from dotenv import load_dotenv
import os
import discord
import asyncio
from classes import MessageWithReactionCount
from utils import replace_user_mentions_with_usernames, ensure_blockquote_in_all_lines, get_channel_messages_past_24_hours, get_messages_with_most_reactions, get_messages_with_attachments_and_reactions

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ART_SHARING_CHANNEL = 1138865343314530324
PROJECT_ART_SHARING_CHANNEL = 1244440385825275955

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True  # Needed to track members who reacted

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Get all messages from #art_sharing in the past 24 hours (9pm UTC yesterday to 9pm UTC today)
    art_sharing_channel = client.get_channel(ART_SHARING_CHANNEL)
    messages = await get_channel_messages_past_24_hours(art_sharing_channel)

    valid_messages_with_attachments_and_reactions: list[MessageWithReactionCount] = await get_messages_with_attachments_and_reactions(messages)
    top_messages = get_messages_with_most_reactions(
        valid_messages_with_attachments_and_reactions, top_n=4)  # select top 4

    # post updates to project_art_sharing_channel
    project_art_sharing_channel = client.get_channel(
        PROJECT_ART_SHARING_CHANNEL)
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
        await project_art_sharing_channel.send(content=msg_2)

        msg_3 = f"{top_message.message.attachments[0].url}"
        await project_art_sharing_channel.send(content=msg_3)

        msg_4 = f"You can find + react to the original post: {top_message.message.jump_url}"
        await project_art_sharing_channel.send(content=msg_4)

        await asyncio.sleep(1)


client.run(DISCORD_BOT_TOKEN)
