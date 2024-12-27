from discord.ext import commands
from constants import PROJECT_ART_SHARING_CHANNEL
import textwrap


async def handle_report_errors_interaction(bot: commands.Bot, traceback: str, post_jump_url: str) -> None:

    project_art_sharing_channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    # limit the traceback to 2000 characters
    traceback_output = textwrap.shorten(traceback, width=1900)
    await project_art_sharing_channel.send(f"⚠️   ⚠️   ⚠️{post_jump_url}\n\n{traceback_output}")


async def handle_report_log_interaction(bot: commands.Bot, message: str) -> None:

    project_art_sharing_channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    await project_art_sharing_channel.send(f"_➜  {message}_", suppress_embeds=True)
