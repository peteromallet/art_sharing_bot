import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import typing
from classes import User
from services.database import insert_user, get_session, get_user, update_user

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD = discord.Object(id=1076117621407223829)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} is connected!")
    await bot.tree.sync(guild=GUILD)


@bot.tree.command(name="update_details", description="Update your details for art sharing", guild=GUILD)
@app_commands.describe(name="Your full name")
@app_commands.describe(youtube_username="Your youtube username")
@app_commands.describe(twitter_username="Your twitter username")
@app_commands.describe(instagram_username="Your instagram username")
@app_commands.describe(website_url="Your website url")
@app_commands.describe(okay_to_feature="Do you want to feature your arts?")
async def update_details(interaction: discord.Interaction, name: typing.Optional[str] = None, youtube_username: typing.Optional[str] = None, twitter_username: typing.Optional[str] = None, instagram_username: typing.Optional[str] = None, website_url: typing.Optional[str] = None, okay_to_feature: typing.Optional[bool] = None):
    new_user = User(id=interaction.user.id, name=name, youtube_username=youtube_username,
                    twitter_username=twitter_username, instagram_username=instagram_username, website_url=website_url, featured=okay_to_feature)

    db_session = get_session()
    existing_user_details: User = get_user(db_session, interaction.user.id)

    if not existing_user_details:
        # set name to discord name by default, if not provided
        if not new_user.name:
            new_user.set_attribute("name", interaction.user.name)

        # set featured to true by default, if not provided
        if new_user.featured == None:
            new_user.set_attribute("featured", True)
        insert_user(db_session, new_user)
    else:
        # update changed attributes only
        # TODO: refactor this dumb logic
        new_user_attributes = list(new_user.__dict__.keys())
        for attribute in new_user_attributes:
            new_attribute_value = getattr(new_user, attribute, None)
            existing_attribute_value = getattr(
                existing_user_details, attribute, None)
            if new_attribute_value is None:
                new_user.set_attribute(attribute, existing_attribute_value)

        update_user(db_session, new_user)

    # send updated details
    new_user_details = get_user(db_session, interaction.user.id)
    db_session.close()

    await interaction.response.send_message(f"## Your details have been updated as follows:\n\n**Name:** {new_user_details.name}\n**Youtube:** {new_user_details.youtube_username}\n**Twitter:** {new_user_details.twitter_username}\n**Instagram:** {new_user_details.instagram_username}\n**Website:** {new_user_details.website_url}\n**Okay To Feature:** {new_user_details.featured}", ephemeral=True)


@bot.tree.command(name="show_details", description="View your details for art sharing", guild=GUILD)
async def show_details(interaction: discord.Interaction):
    db_session = get_session()
    user_details: User = get_user(db_session, interaction.user.id)
    db_session.close()

    if not user_details:
        await interaction.response.send_message("⚠️ You haven't updated your details yet. Type `/update_details`", ephemeral=True)
    else:
        await interaction.response.send_message(f"## Your current details are as follows:\n**Name:** {user_details.name}\n**Youtube:** {user_details.youtube_username}\n**Twitter:** {user_details.twitter_username}\n**Instagram:** {user_details.instagram_username}\n**Website:** {user_details.website_url}\n**Okay To Feature:** {'False' if user_details.featured == None else user_details.featured }", ephemeral=True)


bot.run(DISCORD_BOT_TOKEN)
