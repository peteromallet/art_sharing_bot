import discord
from classes import User
from services.database import insert_user, get_session, get_user, update_user


async def handle_update_details(interaction: discord.Interaction, new_user: User):
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