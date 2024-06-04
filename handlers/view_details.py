import discord
from classes import User
from services.database import get_session, get_user
from utils import convert_user_to_markdown


async def handle_view_details(interaction: discord.Interaction):
    db_session = get_session()
    user_details: User = get_user(db_session, interaction.user.id)
    db_session.close()

    if not user_details:
        await interaction.response.send_message("⚠️ You haven't updated your details yet. Type `/update_details`", ephemeral=True)
    else:
        await interaction.response.send_message(f"## Your current details are as follows:\n{convert_user_to_markdown(user_details)}", ephemeral=True)
