from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
import asyncio
import traceback
from datetime import datetime, timezone

from interaction_handlers.notify_user_dm import handle_notify_user_interaction
from interaction_handlers.view_update_details import handle_view_update_details_interaction
from interaction_handlers.display_top_posts import handle_display_top_posts_interaction, handle_get_top_valid_messages_with_attachments_and_reactions
from interaction_handlers.logging import handle_report_errors_interaction, handle_report_log_interaction

from shared.models import MessageWithReactionCount, SocialMediaPost, SocialMedia
from shared.insert_or_update_user import handle_update_details
from shared.utils import create_post_caption

from services.database import get_db_session, init_db
from services.post_to_twitter import post_to_twitter

from schemas.user import User
from schemas.post import Post

from constants import GUILD_ID, MIN_REACTION_COUNT_TO_DISPLAY_IN_ART_UPDATES, MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD = discord.Object(id=GUILD_ID)  # banodoco

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


@tasks.loop(time=datetime.now(timezone.utc).replace(hour=18, minute=0, second=0, microsecond=0).time())
# @tasks.loop(time=datetime.now(timezone.utc).replace(hour=20, minute=0, second=0, microsecond=0).time())
async def execute_at_8_pm_utc():
    top_6_messages: list[MessageWithReactionCount] = await handle_get_top_valid_messages_with_attachments_and_reactions(bot=bot, top_n=6, min_reaction_count=MIN_REACTION_COUNT_TO_DISPLAY_IN_ART_UPDATES)

    # TODO: post top posts to discord
    await handle_display_top_posts_interaction(bot=bot, top_messages=top_6_messages)
    await handle_report_log_interaction(bot=bot, message=f"{len(top_6_messages)} posts were posted to art_sharing (Top 6, minimum {MIN_REACTION_COUNT_TO_DISPLAY_IN_ART_UPDATES} reactions)")

    db_session = get_db_session()

    for top_message in top_6_messages:
        try:
            user_id = top_message.message.author.id
            # user_id = 688343645644259328  # TODO: don't hardcode
            user_details: User = await db_session.get(User, user_id)

            if not user_details:
                # user hasn't updated their details, so we add it to the database
                new_user = User(id=user_id,
                                name=top_message.message.author.global_name, featured=True, dm_notifications=True)
                user_details = await handle_update_details(new_user=new_user)

            # check if user wants to be featured
            if user_details.featured:
                if user_details.dm_notifications:
                    await handle_notify_user_interaction(bot=bot, message=top_message.message, user_details=user_details)
                    await handle_report_log_interaction(bot=bot, message=f"{user_details.name} received DM for {top_message.message.jump_url}")
                else:
                    await handle_report_log_interaction(bot=bot, message=f"{user_details.name} did not receive DM for {top_message.message.jump_url} (Notifications disabled)")

            # break  # TODO: remove
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc())

    await db_session.close()


@tasks.loop(time=datetime.now(timezone.utc).replace(hour=19, minute=50, second=0, microsecond=0).time())
# @tasks.loop(time=datetime.now(timezone.utc).replace(hour=19, minute=0, second=0, microsecond=0).time())
# @tasks.loop(time=datetime.now(timezone.utc).replace(hour=21, minute=0, second=0, microsecond=0).time())
async def execute_at_9_pm_utc():

    top_4_messages: list[MessageWithReactionCount] = await handle_get_top_valid_messages_with_attachments_and_reactions(bot=bot, top_n=4, min_reaction_count=MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA)

    top_4_messages = top_4_messages[1:]

    await handle_report_log_interaction(bot=bot, message=f"{len(top_4_messages)} posts will be posted to social media (Top 4, minimum {MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA} reactions)")

    db_session = get_db_session()

    social_media_posts: list[SocialMediaPost] = []

    for top_message in top_4_messages:
        try:
            # user_id = 688343645644259328  # TODO: don't hardcode
            user_id = top_message.message.author.id
            user_details: User = await db_session.get(User, user_id)

            # outlier user (new user, got in top 4 in less than 1 hour), reject for now
            if not user_details:
                continue

            # check if user wants to be featured
            elif user_details.featured:
                post_id = top_message.message.id
                comment = top_message.message.content or ""

                # set updated comment, if any
                comment_txt_file_path = os.path.join("temp", f"{post_id}.txt")
                if os.path.exists(comment_txt_file_path):
                    with open(comment_txt_file_path, 'r', encoding='utf-8') as file:
                        comment = file.read()

                    # remove temp file
                    os.remove(comment_txt_file_path)

                # save to database
                post: Post = Post(id=top_message.message.id, reaction_count=top_message.unique_reactions_count,
                                  comment=comment)
                user_details.posts.append(post)

                await db_session.commit()
                await db_session.close()

                # create social media post object
                post_caption = create_post_caption(
                    comment=comment, platform=SocialMedia.TWITTER, user_details=user_details)
                social_media_post = SocialMediaPost(
                    post_id=top_message.message.id, attachment_url=top_message.message.attachments[0].url, caption=post_caption, attachment_name=top_message.message.attachments[0].filename, post_jump_url=top_message.message.jump_url)
                social_media_posts.append(social_media_post)

            # break  # TODO: remove
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc())

    # TODO: schedule posts to social media, every 15 minutes
    for social_media_post in social_media_posts:
        try:
            await post_to_twitter(social_media_post)
            await handle_report_log_interaction(bot=bot, message=f"Posted {social_media_post.post_jump_url} to Twitter")

            await asyncio.sleep(15*60)
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc())


@bot.event
async def on_ready():
    try:
        print(f'Logged in as {bot.user}')
        await handle_report_log_interaction(bot=bot, message=f"{bot.user} has started up!")
        await bot.tree.sync()

        if os.path.exists('./database.db'):
            # os.remove('./database.db')
            pass
        else:
            await init_db()

        # execute_at_8_pm_utc.start()
        execute_at_9_pm_utc.start()

    except Exception:
        await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc())


@bot.tree.command(name="art_sharing_details", description="View and update your art sharing details")
async def view_update_details(interaction: discord.Interaction):
    try:
        await handle_view_update_details_interaction(bot=bot, interaction=interaction)
        await handle_report_log_interaction(bot=bot, message=f"{interaction.user.global_name} used the `/art_sharing_details` command")
    except Exception:
        await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc())

bot.run(DISCORD_BOT_TOKEN)
