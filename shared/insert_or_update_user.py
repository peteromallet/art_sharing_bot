import discord
from services.database import get_db_session
from schemas.user import User


async def handle_update_details(new_user: User, interaction: discord.Interaction) -> User:
    db_session = get_db_session()
    existing_user_details: User = await db_session.get(User, interaction.user.id)

    if not existing_user_details:
        # set name to discord name by default, if not provided
        if not new_user.name:
            new_user.name = interaction.user.global_name

        # set featured to true by default, if not provided
        if new_user.featured == None:
            new_user.featured = True

        await db_session.add(new_user)
    else:
        # update changed attributes only
        new_user_attributes = list(
            filter(lambda x: not x.startswith('_'), new_user.__dict__.keys()))
        for attribute in new_user_attributes:
            new_attribute_value = getattr(new_user, attribute, None)
            if new_attribute_value != existing_user_details.__dict__.get(attribute):
                setattr(existing_user_details,
                        attribute, new_attribute_value)

    await db_session.commit()
    updated_user = await db_session.get(User, interaction.user.id)
    await db_session.close()

    return updated_user