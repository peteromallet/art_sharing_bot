import discord
from classes import User
from services.database import get_session, get_user


async def handle_view_details(interaction: discord.Interaction):
    db_session = get_session()
    user_details: User = get_user(db_session, interaction.user.id)
    db_session.close()

    if not user_details:
        await interaction.response.send_message("⚠️ You haven't updated your details yet. Type `/update_details`", ephemeral=True)
    else:
        await interaction.response.send_message(f"## Your current details are as follows:\n**Name:** {user_details.name}\n**Youtube:** {user_details.youtube_username}\n**Twitter:** {user_details.twitter_username}\n**Instagram:** {user_details.instagram_username}\n**Website:** {user_details.website_url}\n**Okay To Feature:** {'False' if user_details.featured == None else user_details.featured }", ephemeral=True)
