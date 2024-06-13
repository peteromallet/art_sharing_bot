import discord
from shared.utils import convert_user_to_markdown
from services.database import get_db_session
from schemas.user import User
from shared.insert_or_update_user import handle_update_details


def format_msg(user_details: User) -> str:
    if user_details.featured:
        msg = f"## Your current details are as follows:\n\n{convert_user_to_markdown(user_details)}\n\n_Please click the buttons below if you'd like to update your details or not be featured_"
    else:
        msg = f"## Your current details are as follows:\n\n{convert_user_to_markdown(user_details)}\n\n_Please click the buttons below if you'd like to update your details or be featured again_"

    return msg


class UpdateDetailsModal(discord.ui.Modal, title='Update personal details'):
    nameInput = discord.ui.TextInput(label='Name', required=True)
    twitterInput = discord.ui.TextInput(label='Twitter', required=False)
    instagramInput = discord.ui.TextInput(label='Instagram', required=False)
    youtubeInput = discord.ui.TextInput(label='Youtube', required=False)
    websiteInput = discord.ui.TextInput(label='Website', required=False)

    def __init__(self, user_details: User):
        super().__init__()
        self.user_details = user_details
        # set default values
        self.nameInput.default = self.user_details.name
        self.twitterInput.default = self.user_details.twitter
        self.instagramInput.default = self.user_details.instagram
        self.youtubeInput.default = self.user_details.youtube
        self.websiteInput.default = self.user_details.website

    async def on_submit(self, interaction: discord.Interaction):
        # update database with new details
        new_user_details = User(id=self.user_details.id, name=self.nameInput.value, twitter=self.twitterInput.value or None, youtube=self.youtubeInput.value or None,
                                instagram=self.instagramInput.value or None, website=self.websiteInput.value or None, featured=self.user_details.featured)

        new_user_details = await handle_update_details(new_user=new_user_details)

        myView = ViewUpdateDetailsView(user_details=new_user_details)
        await interaction.response.edit_message(content=format_msg(new_user_details), view=myView)


class ViewUpdateDetailsView(discord.ui.View):
    def __init__(self, user_details: User):
        super().__init__()
        self.timeout = None
        self.user_details = user_details
        self.children[1].label = "Stop being featured" if self.user_details.featured else "Allow to be featured"
        self.children[1].style = discord.ButtonStyle.red if self.user_details.featured else discord.ButtonStyle.green

    @discord.ui.button(label="Edit Details", style=discord.ButtonStyle.blurple)
    async def open_details_modal(self, interaction: discord.Interaction, _):
        updateDetailsModal = UpdateDetailsModal(self.user_details)
        await interaction.response.send_modal(updateDetailsModal)

    @discord.ui.button()
    async def edit_featuring(self, interaction: discord.Interaction, _):
        new_user = User(id=self.user_details.id, name=self.user_details.name, twitter=self.user_details.twitter,
                        instagram=self.user_details.instagram, youtube=self.user_details.youtube, website=self.user_details.website, featured=not self.user_details.featured)  # toggle featured

        # update database with new details
        self.user_details = await handle_update_details(new_user=new_user)

        myView = ViewUpdateDetailsView(user_details=self.user_details)
        await interaction.response.edit_message(content=format_msg(self.user_details), view=myView)


async def handle_view_update_details_interaction(interaction: discord.Interaction):
    db_session = get_db_session()
    user_details: User = await db_session.get(User, interaction.user.id)
    await db_session.close()

    if not user_details:
        user_details = User(id=interaction.user.id,
                            name=interaction.user.global_name, featured=True)

    myView = ViewUpdateDetailsView(user_details)
    await interaction.response.send_message(format_msg(user_details), view=myView, ephemeral=True, delete_after=60)
