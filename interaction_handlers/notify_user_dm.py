import discord
from discord.ext import commands
from shared.utils import convert_user_to_markdown

from shared.insert_or_update_user import handle_update_details
from schemas.user import User
from .logging import handle_report_log_interaction

# send dm to user
# Edit personal details - opens a modal for editing personal details
# Edit featuring - dynamic button for changing featuring


class DataSharer():
    def __init__(self, comment: str = "", jump_url: str = "", user_details: User = None, bot: commands.Bot = None):
        self.comment = comment
        self.jump_url = jump_url
        self.user_details = user_details
        self.bot = bot


def format_msg(dataSharer: DataSharer) -> str:
    msg = f"## Your art may be featured on Banodoco's social channels today: {dataSharer.jump_url}\n\nYour current details are as follows:\n\n{convert_user_to_markdown(dataSharer.user_details)}\n**Comment:** {dataSharer.comment}\n\n_Please click the buttons below if you'd like to update your details,"

    if dataSharer.user_details.featured:
        msg += " or not be featured_"
    else:
        msg += " or be featured again_"

    return msg


class UpdateDetailsModal(discord.ui.Modal, title='Update personal details'):
    # nameInput = discord.ui.TextInput(label='Name', required=True)
    twitterInput = discord.ui.TextInput(
        label='Twitter handle (e.g @john_doe)', required=False, placeholder='@twitter_handle')
    instagramInput = discord.ui.TextInput(
        label='Instagram handle (e.g @john_doe)', required=False, placeholder='@instagram_handle')
    youtubeInput = discord.ui.TextInput(
        label='Youtube handle (e.g @john_doe)', required=False, placeholder='@youtube_handle')
    tiktokInput = discord.ui.TextInput(
        label='Tiktok handle (e.g @john_doe)', required=False, placeholder='@tiktok_handle')
    websiteInput = discord.ui.TextInput(
        label='Website', required=False, placeholder='https://website.com')

    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.dataSharer = dataSharer
        # set default values
        self.twitterInput.default = self.dataSharer.user_details.twitter
        self.instagramInput.default = self.dataSharer.user_details.instagram
        self.youtubeInput.default = self.dataSharer.user_details.youtube
        self.tiktokInput.default = self.dataSharer.user_details.tiktok
        self.websiteInput.default = self.dataSharer.user_details.website

    async def on_submit(self, interaction: discord.Interaction):
        new_user = User(id=self.dataSharer.user_details.id, name=interaction.user.global_name, twitter=self.twitterInput.value or None,
                        instagram=self.instagramInput.value or None, youtube=self.youtubeInput.value or None, tiktok=self.tiktokInput.value or None, website=self.websiteInput.value or None, featured=self.dataSharer.user_details.featured, dm_notifications=self.dataSharer.user_details.dm_notifications)
        # update database with new details
        new_user_details = await handle_update_details(new_user=new_user)
        self.dataSharer.user_details = new_user_details

        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.dataSharer.bot, message=f"{interaction.user.global_name} updated personal details from {self.dataSharer.jump_url} via DM")


class MyView(discord.ui.View):
    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.timeout = None
        self.dataSharer = dataSharer
        self.user_details = self.dataSharer.user_details
        self.children[1].label = "Stop being featured" if self.user_details.featured else "Allow to be featured"
        self.children[1].style = discord.ButtonStyle.red if self.user_details.featured else discord.ButtonStyle.green

        self.bot = self.dataSharer.bot

    @discord.ui.button(label="Edit Details", style=discord.ButtonStyle.blurple, emoji="📝")
    async def open_details_modal(self, interaction: discord.Interaction, _):
        updateDetailsModal = UpdateDetailsModal(self.dataSharer)
        await interaction.response.send_modal(updateDetailsModal)

    @discord.ui.button(emoji="✨")
    async def edit_featuring(self, interaction: discord.Interaction, _):
        new_user = User(id=self.dataSharer.user_details.id, name=interaction.user.global_name, twitter=self.user_details.twitter,
                        instagram=self.user_details.instagram, youtube=self.user_details.youtube, tiktok=self.user_details.tiktok, website=self.user_details.website, dm_notifications=self.dataSharer.user_details.dm_notifications, featured=not self.dataSharer.user_details.featured)  # toggle featured
        # update database with new details
        self.dataSharer.user_details = await handle_update_details(new_user=new_user)

        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.dataSharer.bot, message=f"{interaction.user.global_name} updated featuring to {self.dataSharer.user_details.featured} for {self.dataSharer.jump_url} via DM")


async def handle_notify_user_interaction(bot: commands.Bot, message: discord.Message, user_details: User):
    dataSharer = DataSharer(
        comment=message.content, jump_url=message.jump_url, user_details=user_details, bot=bot)
    myView = MyView(dataSharer)

    # user = await bot.fetch_user(user_details.id)  # TODO: use author.send
    # await user.send(format_msg(dataSharer), view=myView, delete_after=3600)

    # delete after 1 hour
    await message.author.send(format_msg(dataSharer), view=myView, delete_after=3600, suppress_embeds=True)
