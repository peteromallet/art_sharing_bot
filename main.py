from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from classes import User, MessageWithReactionCount

from handlers.view_details import handle_view_details_interaction
from handlers.update_details import handle_update_details_interaction
from handlers.notify_user_dm import handle_notify_user_interaction
from handlers.update_featuring import handle_update_featuring_interaction

from services.database import get_session, get_user

from utils import replace_user_mentions_with_usernames, ensure_blockquote_in_all_lines, get_channel_messages_past_24_hours, get_messages_with_most_reactions, get_messages_with_attachments_and_reactions


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


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

    art_sharing_channel = bot.get_channel(ART_SHARING_CHANNEL)
    messages = await get_channel_messages_past_24_hours(art_sharing_channel)
    valid_messages_with_attachments_and_reactions: list[MessageWithReactionCount] = await get_messages_with_attachments_and_reactions(messages)

    db_session = get_session()
    user_details: User = get_user(db_session, 688343645644259328)

    # TODO: check if user wants to be featured
    await handle_notify_user_interaction(bot, valid_messages_with_attachments_and_reactions[2].message, user_details)


@bot.tree.command(name="show_details", description="View your details for art sharing")
async def show_details(interaction: discord.Interaction):
    await handle_view_details_interaction(interaction=interaction)


@bot.tree.command(name="update_details", description="Update your details for art sharing")
@app_commands.describe(name="Your full name")
@app_commands.describe(youtube="Your youtube username")
@app_commands.describe(twitter="Your twitter username")
@app_commands.describe(instagram="Your instagram username")
@app_commands.describe(website="Your website url")
@app_commands.describe(okay_to_feature="Do you want to feature your arts?")
async def update_details(interaction: discord.Interaction, name: Optional[str] = None, youtube: Optional[str] = None, twitter: Optional[str] = None, instagram: Optional[str] = None, website: Optional[str] = None, okay_to_feature: Optional[bool] = None):
    new_user = User(id=interaction.user.id, name=name, youtube=youtube,
                    twitter=twitter, instagram=instagram, website=website, featured=okay_to_feature)
    await handle_update_details_interaction(interaction=interaction, new_user=new_user)


@bot.tree.command(name="update_featuring", description="Enable or disable your art featuring")
@app_commands.describe(okay_to_feature="Do you want to feature your arts?")
async def update_details(interaction: discord.Interaction, okay_to_feature: bool):
    await handle_update_featuring_interaction(interaction=interaction, okay_to_feature=okay_to_feature)

bot.run(DISCORD_BOT_TOKEN)
