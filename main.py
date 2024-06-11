from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
# from classes import User, MessageWithReactionCount

from interaction_handlers.notify_user_dm import handle_notify_user_interaction
from interaction_handlers.view_update_details import handle_view_update_details_interaction
import asyncio
from datetime import datetime, timezone

from services.database import get_db_session, init_db
from shared.models import MessageWithReactionCount

from shared.utils import replace_user_mentions_with_usernames, ensure_blockquote_in_all_lines, get_channel_messages_past_24_hours, get_messages_with_most_reactions, get_messages_with_attachments_and_reactions

from schemas.user import User
from schemas.post import Post


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ART_SHARING_CHANNEL = 1138865343314530324
PROJECT_ART_SHARING_CHANNEL = 1244440385825275955
GUILD = discord.Object(id=1076117621407223829)  # banodoco

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


# @tasks.loop(time=datetime.now(timezone.utc).replace(hour=20, minute=0, second=0, microsecond=0).time())
@tasks.loop(time=datetime.now(timezone.utc).replace(hour=9, minute=7, second=0, microsecond=0).time())
async def execute_at_8_pm_utc():
    channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    # await channel.send("hi from execute_at_8_pm_utc")
    asyncio.create_task(post_video_twitter(channel))
    asyncio.create_task(post_video_youtube(channel))

    # retrieve top 6 posts from art sharing channel
    # send dm to each top artists


@tasks.loop(time=datetime.now(timezone.utc).replace(hour=21, minute=0, second=0, microsecond=0).time())
async def execute_at_9_pm_utc():
    pass
    # channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    # await channel.send("hi from execute_at_9_pm_utc")
    # retrieve top 4 posts from art sharing channel
    # schedule posts to social media, every 15 minutes


async def post_video_twitter(channel: discord.TextChannel):
  # Your list of messages
    messages = [1, 2, 3]

    for message in messages:
        await channel.send(f"Posting video {message} to twitter, in background inside execute_at_8_pm_utc...{datetime.now().time()}")
        await asyncio.sleep(5)


async def post_video_youtube(channel: discord.TextChannel):
  # Your list of messages
    messages = [1, 2, 3]

    for message in messages:
        await channel.send(f"Posting video {message} to youtube, in background inside execute_at_8_pm_utc...{datetime.now().time()}")
        await asyncio.sleep(5)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # await bot.tree.sync()

    if not os.path.exists('./database.db'):
        await init_db()

    # db_session = get_db_session()
    # user = User(id=123223, name="Yuvraj", website="www.google.com")
    # db_session.add(user)

    # existing_user = await db_session.get(User, 123223)
    # existing_user.featured = False
    # print(existing_user)
    # await db_session.commit()
    # await db_session.close()
    # execute_at_8_pm_utc.start()
    # execute_at_9_pm_utc.start()

    # channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)

    # post_videos(channel)
    # await channel.send("execution continues on_ready..")
    # Run the scheduled task

    art_sharing_channel = bot.get_channel(ART_SHARING_CHANNEL)
    messages = await get_channel_messages_past_24_hours(art_sharing_channel)
    valid_messages_with_attachments_and_reactions: list[MessageWithReactionCount] = await get_messages_with_attachments_and_reactions(messages)

    message = valid_messages_with_attachments_and_reactions[0].message
    db_session = get_db_session()
    post: Post = Post(id=message.id, reaction_count=valid_messages_with_attachments_and_reactions[
                      0].unique_reactions_count, comment=message.content, user_id=6883436456442259328)
    db_session.add(post)
    await db_session.commit()
    await db_session.close()

    # # user_details: User = get_user(db_session, 301463647895683072)
    # user_details: User = await db_session.get(User, 688343645644259328)

    # message.content = replace_user_mentions_with_usernames(message)

    # # # TODO: check if user wants to be featured
    # await handle_notify_user_interaction(bot, message, user_details)


@bot.tree.command(name="art_sharing_details", description="View and update your art sharing details")
async def view_update_details(interaction: discord.Interaction):
    await handle_view_update_details_interaction(interaction=interaction)

bot.run(DISCORD_BOT_TOKEN)
