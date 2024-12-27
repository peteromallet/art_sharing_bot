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
from shared.utils import create_post_caption, download_file, replace_channel_mentions_with_names

from services.database import get_db_session, init_db
from services.post_to_twitter import post_to_twitter
from services.zapier import post_to_instagram, post_to_tiktok_via_buffer, post_to_youtube
from services.youtube_title_generator import create_youtube_title_using_claude

from schemas.user import User
from schemas.post import Post

from constants import GUILD_ID, MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA

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
async def execute_at_8_pm_utc():
    top_4_messages: list[MessageWithReactionCount] = await handle_get_top_valid_messages_with_attachments_and_reactions(bot=bot, top_n=4, min_reaction_count=MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA)

    await handle_report_log_interaction(bot=bot, message=f"{len(top_4_messages)} posts will be SURELY posted to #art_updates + ig/twitter/yt/tiktok (Top 4, minimum {MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA} reactions)")

    db_session = get_db_session()

    messaged_users = []
    for top_message in top_4_messages:
        try:
            user_id = top_message.message.author.id
            # user_id = 688343645644259328  # TODO: don't hardcode

            user_details: User = await db_session.get(User, user_id)

            if user_details:
                # user was added to database by the bot (check 2 -> USER didn't update details)
                if user_details.created_at == user_details.updated_at:
                    if user_id not in messaged_users:
                        await handle_notify_user_interaction(bot=bot, message=top_message.message, user_details=user_details)
                        await handle_report_log_interaction(bot=bot, message=f"{user_details.name} received DM for {top_message.message.jump_url} (Existing User, Not updated personal details)")
                        messaged_users.append(user_id)
                else:
                    await handle_report_log_interaction(bot=bot, message=f"{user_details.name} did not receive DM for {top_message.message.jump_url} (Existing User, already updated personal details)")

            # user hasn't updated their details, so we add it to the database (check 1 -> NEW USER)
            else:
                new_user = User(id=user_id,
                                # TODO: don't hardcode
                                # name="yuvraj hardcoded", featured=True, dm_notifications=True)
                                name=top_message.message.author.global_name, featured=True, dm_notifications=True)
                user_details = await handle_update_details(new_user=new_user)
                await handle_notify_user_interaction(bot=bot, message=top_message.message, user_details=user_details)
                await handle_report_log_interaction(bot=bot, message=f"{user_details.name} received DM for {top_message.message.jump_url} (New User)")
                messaged_users.append(user_id)

            # break  # TODO: remove
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=top_message.message.jump_url)

    await db_session.close()


@tasks.loop(time=datetime.now(timezone.utc).replace(hour=19, minute=0, second=0, microsecond=0).time())
async def execute_at_9_pm_utc():

    top_4_messages: list[MessageWithReactionCount] = await handle_get_top_valid_messages_with_attachments_and_reactions(bot=bot, top_n=4, min_reaction_count=MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA)

    await handle_display_top_posts_interaction(bot=bot, top_messages=top_4_messages)

    await handle_report_log_interaction(bot=bot, message=f"{len(top_4_messages)} posts will be posted to yt/twitter/ig/tiktok (Top 4, minimum {MIN_REACTION_COUNT_TO_DISPLAY_IN_SOCIAL_MEDIA} reactions)")

    db_session = get_db_session()

    social_media_posts: list[SocialMediaPost] = []

    for top_message in top_4_messages:
        post_jump_url = top_message.message.jump_url

        try:
            # user_id = 688343645644259328  # TODO: don't hardcode
            user_id = top_message.message.author.id
            user_details: User = await db_session.get(User, user_id)

            # shouldn't happen, keeping this just in case
            if not user_details:
                continue

            # check if user wants to be featured
            elif user_details.featured:
                post_id = top_message.message.id
                comment = top_message.message.content or ""
                comment = replace_channel_mentions_with_names(
                    top_message.message)

                # save to database
                post: Post = Post(id=post_id, reaction_count=top_message.unique_reactions_count,
                                  comment=comment)
                user_details.posts.append(post)

                await db_session.commit()  # TODO: uncomment
                await db_session.close()

                # download the attachment
                attachment_name = top_message.message.attachments[0].filename
                attachment_url = top_message.message.attachments[0].url
                file_local_path = os.path.join('temp', attachment_name)
                await download_file(url=attachment_url,  save_path=file_local_path)

                try:
                    ai_video_title = create_youtube_title_using_claude(
                        file_local_path=file_local_path, original_comment=comment, post_id=post_id)
                except Exception:
                    # use default title
                    ai_video_title = "Featured piece by"
                    await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=post_jump_url)

                # create social media post object
                twitter_caption = create_post_caption(
                    comment=comment, platform=SocialMedia.TWITTER, user_details=user_details, ai_title=ai_video_title)
                instagram_video_caption = create_post_caption(
                    comment=comment, platform=SocialMedia.INSTAGRAM, user_details=user_details, ai_title=ai_video_title)
                tiktok_video_caption = create_post_caption(
                    comment=comment, platform=SocialMedia.TIKTOK, user_details=user_details, ai_title=ai_video_title)
                youtube_video_caption = create_post_caption(
                    comment=comment, platform=SocialMedia.YOUTUBE, user_details=user_details, ai_title=ai_video_title)

                # use name instead of handle
                youtube_video_title = f"\"{ai_video_title}\" by {user_details.name}"

                social_media_post = SocialMediaPost(
                    post_id=post_id, attachment_url=attachment_url, caption_twitter=twitter_caption, video_caption_instagram=instagram_video_caption, video_caption_tiktok=tiktok_video_caption, video_description_youtube=youtube_video_caption, video_title_youtube=youtube_video_title, attachment_name=attachment_name, post_jump_url=post_jump_url, local_path=file_local_path)
                social_media_posts.append(social_media_post)

            # break  # TODO: remove
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=post_jump_url)

    # schedule posts to social media, every 15 minutes
    for social_media_post in social_media_posts:
        try:
            file_extension = os.path.splitext(
                social_media_post.attachment_name)[1]

            # post to twitter
            try:
                tweet_url = await post_to_twitter(social_media_post)
                await handle_report_log_interaction(bot=bot, message=f"Posted {social_media_post.post_jump_url} to Twitter: <{tweet_url}>")
            except Exception:
                await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=social_media_post.post_jump_url)

            if file_extension != '.gif':
                # post to youtube
                try:
                    # zapier will report back to discord
                    post_to_youtube(social_media_post)
                except Exception:
                    await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=social_media_post.post_jump_url)

                # post to instagram reels
                try:
                    # zapier will report back to discord
                    post_to_instagram(social_media_post)
                except Exception:
                    await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=social_media_post.post_jump_url)

                # post videos to tiktok via buffer
                try:
                    post_to_tiktok_via_buffer(social_media_post)
                    await handle_report_log_interaction(bot=bot, message=f"Posted {social_media_post.post_jump_url} to tiktok (hopefully)")
                except Exception:
                    await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=social_media_post.post_jump_url)

            # delete local file
            os.remove(social_media_post.local_path)

            # sleep 15 minutes
            await asyncio.sleep(15*60)
        except Exception:
            await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url=social_media_post.post_jump_url)


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

        execute_at_8_pm_utc.start()
        execute_at_9_pm_utc.start()

    except Exception:
        await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url="")


@ bot.tree.command(name="art_sharing_details", description="View and update your art sharing details")
async def view_update_details(interaction: discord.Interaction):
    try:
        await handle_view_update_details_interaction(bot=bot, interaction=interaction)
        await handle_report_log_interaction(bot=bot, message=f"{interaction.user.global_name} used the `/art_sharing_details` command")
    except Exception:
        await handle_report_errors_interaction(bot=bot, traceback=traceback.format_exc(), post_jump_url="")

bot.run(DISCORD_BOT_TOKEN)
