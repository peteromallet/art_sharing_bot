from discord.ext import commands
from constants import PROJECT_ART_SHARING_CHANNEL


async def handle_report_errors_interaction(bot: commands.Bot, traceback: str) -> None:

    project_art_sharing_channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    # limit the traceback to 2000 characters
    await project_art_sharing_channel.send(f"⚠️   ⚠️   ⚠️\n\n{traceback[:2000]}")


async def handle_report_log_interaction(bot: commands.Bot, message: str) -> None:

    project_art_sharing_channel = bot.get_channel(PROJECT_ART_SHARING_CHANNEL)
    await project_art_sharing_channel.send(f"_➜  {message}_", suppress_embeds=True)
