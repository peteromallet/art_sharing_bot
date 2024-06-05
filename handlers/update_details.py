import discord
from classes import User
from services.database import insert_user, get_session, get_user, update_user
from utils import convert_user_to_markdown


async def handle_update_details_interaction(interaction: discord.Interaction, new_user: User):
    new_user_details = handle_update_details(
        new_user=new_user, interaction=interaction)

    await interaction.response.send_message(f"## Your details have been updated as follows:\n{convert_user_to_markdown(new_user_details)}", ephemeral=True)


# creates or updates user details
def handle_update_details(new_user: User, interaction: discord.Interaction) -> User:
    db_session = get_session()
    existing_user_details: User = get_user(
        session=db_session, user_id=interaction.user.id)

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
        # TODO: refactor this dumb ORM logic
        new_user_attributes = list(new_user.__dict__.keys())
        for attribute in new_user_attributes:
            new_attribute_value = getattr(new_user, attribute, None)
            existing_attribute_value = getattr(
                existing_user_details, attribute, None)
            if new_attribute_value is None:
                new_user.set_attribute(attribute, existing_attribute_value)

        update_user(db_session, new_user)

    # send updated details
    new_user_details = get_user(
        session=db_session, user_id=interaction.user.id)
    db_session.close()

    return new_user_details
