import discord
from classes import User
from services.database import get_session, get_user, update_user


async def handle_update_featuring_interaction(interaction: discord.Interaction, okay_to_feature: bool):
    success = handle_update_featuring(interaction=interaction,
                                      okay_to_feature=okay_to_feature)

    if not success:
        await interaction.response.send_message("Your arts have not been featured yet, you can't use this command", ephemeral=True)

    else:
        msg = "You'll no longer be featured on Banodoco's social channels" if not okay_to_feature else "You'll be featured on Banodoco's social channels from now on"
        await interaction.response.send_message(msg, ephemeral=True)


def handle_update_featuring(interaction: discord.Interaction, okay_to_feature: bool) -> bool:
    db_session = get_session()
    existing_user_details: User = get_user(
        session=db_session, user_id=interaction.user.id)

    if not existing_user_details:
        # prevent unchosen users from using this feature
        return False
    else:
        # TODO: fix the shit mapper
        new_user_details = User(id=existing_user_details.id, name=existing_user_details.name,
                                youtube=existing_user_details.youtube, website=existing_user_details.website,
                                twitter=existing_user_details.twitter, instagram=existing_user_details.instagram, featured=okay_to_feature)
        update_user(db_session, new_user_details)
        return True
