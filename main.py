from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from classes import User

from handlers.view_details import handle_view_details
from handlers.update_details import handle_update_details

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ART_SHARING_CHANNEL = 1138865343314530324
PROJECT_ART_SHARING_CHANNEL = 1244440385825275955
GUILD = discord.Object(id=1076117621407223829)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync(guild=GUILD)


@bot.tree.command(name="show_details", description="View your details for art sharing", guild=GUILD)
async def show_details(interaction: discord.Interaction):
    await handle_view_details(interaction)


@bot.tree.command(name="update_details", description="Update your details for art sharing", guild=GUILD)
@app_commands.describe(name="Your full name")
@app_commands.describe(youtube_username="Your youtube username")
@app_commands.describe(twitter_username="Your twitter username")
@app_commands.describe(instagram_username="Your instagram username")
@app_commands.describe(website_url="Your website url")
@app_commands.describe(okay_to_feature="Do you want to feature your arts?")
async def update_details(interaction: discord.Interaction, name: Optional[str] = None, youtube_username: Optional[str] = None, twitter_username: Optional[str] = None, instagram_username: Optional[str] = None, website_url: Optional[str] = None, okay_to_feature: Optional[bool] = None):
    new_user = User(id=interaction.user.id, name=name, youtube_username=youtube_username,
                    twitter_username=twitter_username, instagram_username=instagram_username, website_url=website_url, featured=okay_to_feature)
    await handle_update_details(interaction, new_user)


bot.run(DISCORD_BOT_TOKEN)
