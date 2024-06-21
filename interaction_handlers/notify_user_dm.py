import discord
from discord.ext import commands
from shared.utils import convert_user_to_markdown
import os

from shared.insert_or_update_user import handle_update_details
from schemas.user import User
from .logging import handle_report_log_interaction

# send dm to user
# Edit comment button - opens a modal for editing comment
# Edit personal details - opens a modal for editing personal details
# Edit featuring - dynamic button for changing featuring


class DataSharer():
    def __init__(self, comment: str = "", file_save_path: str = "", jump_url: str = "", user_details: User = None, bot: commands.Bot = None):
        self.comment = comment
        self.file_save_path = file_save_path
        self.jump_url = jump_url
        self.user_details = user_details
        self.bot = bot


def format_msg(dataSharer: DataSharer) -> str:
    msg = f"## Your art may be featured on Banodoco's social channels today: {dataSharer.jump_url}\n\nYour current details are as follows:\n\n{convert_user_to_markdown(dataSharer.user_details)}\n**Comment:** {dataSharer.comment}\n\n_Please click the buttons below if you'd like to update your details,"

    if dataSharer.user_details.dm_notifications:
        msg += " disable notifications"
    else:
        msg += " enable notifications"
    if dataSharer.user_details.featured:
        msg += " or not be featured_"
    else:
        msg += " or be featured again_"

    return msg


class UpdateCommentModal(discord.ui.Modal, title='Update comment'):
    commentInput = discord.ui.TextInput(
        label='Comment', style=discord.TextStyle.paragraph)

    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.dataSharer = dataSharer

        # set updated comment, if any
        if os.path.exists(self.dataSharer.file_save_path):
            with open(self.dataSharer.file_save_path, 'r',  encoding='utf-8') as file:
                edited_comment = file.read()
                self.dataSharer.comment = edited_comment
                self.commentInput.default = edited_comment
        else:
            self.commentInput.default = self.dataSharer.comment

    async def on_submit(self, interaction: discord.Interaction):
        # update txt file with new comment
        with open(self.dataSharer.file_save_path, 'w', encoding='utf-8') as file:
            file.write(self.commentInput.value)

        self.dataSharer.comment = self.commentInput.value
        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.dataSharer.bot, message=f"{interaction.user.global_name} updated comment for {self.dataSharer.jump_url} via DM")


class UpdateDetailsModal(discord.ui.Modal, title='Update personal details'):
    nameInput = discord.ui.TextInput(label='Name', required=True)
    twitterInput = discord.ui.TextInput(
        label='Twitter handle (e.g @john_doe)', required=False, placeholder='@twitter_handle')
    instagramInput = discord.ui.TextInput(
        label='Instagram handle (e.g @john_doe)', required=False, placeholder='@instagram_handle')
    youtubeInput = discord.ui.TextInput(
        label='Youtube handle (e.g @john_doe)', required=False, placeholder='@youtube_handle')
    websiteInput = discord.ui.TextInput(
        label='Website', required=False, placeholder='https://website.com')

    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.dataSharer = dataSharer
        # set default values
        self.nameInput.default = self.dataSharer.user_details.name
        self.twitterInput.default = self.dataSharer.user_details.twitter
        self.instagramInput.default = self.dataSharer.user_details.instagram
        self.youtubeInput.default = self.dataSharer.user_details.youtube
        self.websiteInput.default = self.dataSharer.user_details.website

    async def on_submit(self, interaction: discord.Interaction):
        new_user = User(id=self.dataSharer.user_details.id, name=self.nameInput.value, twitter=self.twitterInput.value or None,
                        instagram=self.instagramInput.value or None, youtube=self.youtubeInput.value or None, website=self.websiteInput.value or None, featured=self.dataSharer.user_details.featured, dm_notifications=self.dataSharer.user_details.dm_notifications)
        # update database with new details
        new_user_details = await handle_update_details(new_user=new_user)
        self.dataSharer.user_details = new_user_details

        # set updated comment, if any
        if os.path.exists(self.dataSharer.file_save_path):
            with open(self.dataSharer.file_save_path, 'r', encoding='utf-8') as file:
                edited_comment = file.read()
                self.dataSharer.comment = edited_comment

        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.dataSharer.bot, message=f"{interaction.user.global_name} updated personal details from {self.dataSharer.jump_url} via DM")


class MyView(discord.ui.View):
    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.timeout = None
        self.dataSharer = dataSharer
        self.user_details = self.dataSharer.user_details
        self.children[3].label = "Stop being featured" if self.user_details.featured else "Allow to be featured"
        self.children[3].style = discord.ButtonStyle.red if self.user_details.featured else discord.ButtonStyle.green
        self.children[2].label = "Disable notifications" if self.user_details.dm_notifications else "Enable notifications"
        self.children[2].style = discord.ButtonStyle.secondary if self.user_details.dm_notifications else discord.ButtonStyle.green

        self.bot = self.dataSharer.bot

        if not self.dataSharer.user_details.featured:  # hide notification button if not featured
            self.remove_item(self.children[2])

    @discord.ui.button(label="Edit Comment", style=discord.ButtonStyle.blurple, emoji="💬")
    async def open_comment_modal(self, interaction: discord.Interaction, _):
        updateCommentModal = UpdateCommentModal(self.dataSharer)
        await interaction.response.send_modal(updateCommentModal)

    @discord.ui.button(label="Edit Details", style=discord.ButtonStyle.blurple, emoji="📝")
    async def open_details_modal(self, interaction: discord.Interaction, _):
        updateDetailsModal = UpdateDetailsModal(self.dataSharer)
        await interaction.response.send_modal(updateDetailsModal)

    @discord.ui.button(emoji="🔔")
    async def edit_notification(self, interaction: discord.Interaction, _):
        new_user = User(id=self.user_details.id, name=self.user_details.name, twitter=self.user_details.twitter,
                        instagram=self.user_details.instagram, youtube=self.user_details.youtube, website=self.user_details.website, featured=self.user_details.featured, dm_notifications=not self.user_details.dm_notifications)  # toggle notification

        # update database with new details
        self.dataSharer.user_details = await handle_update_details(new_user=new_user)

        # set updated comment, if any
        if os.path.exists(self.dataSharer.file_save_path):
            with open(self.dataSharer.file_save_path, 'r', encoding='utf-8') as file:
                edited_comment = file.read()
                self.dataSharer.comment = edited_comment

        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.bot, message=f"{interaction.user.global_name} updated notification to {self.user_details.dm_notifications} for {self.dataSharer.jump_url} via DM")

    @discord.ui.button(emoji="✨")
    async def edit_featuring(self, interaction: discord.Interaction, _):
        new_user = User(id=self.dataSharer.user_details.id, name=self.user_details.name, twitter=self.user_details.twitter,
                        instagram=self.user_details.instagram, youtube=self.user_details.youtube, website=self.user_details.website, dm_notifications=self.dataSharer.user_details.dm_notifications, featured=not self.dataSharer.user_details.featured)  # toggle featured
        # update database with new details
        self.dataSharer.user_details = await handle_update_details(new_user=new_user)

        # set updated comment, if any
        if os.path.exists(self.dataSharer.file_save_path):
            with open(self.dataSharer.file_save_path, 'r', encoding='utf-8') as file:
                edited_comment = file.read()
                self.dataSharer.comment = edited_comment

        myView = MyView(dataSharer=self.dataSharer)
        await interaction.response.edit_message(content=format_msg(self.dataSharer), view=myView, delete_after=3600)
        await handle_report_log_interaction(bot=self.dataSharer.bot, message=f"{interaction.user.global_name} updated featuring to {self.dataSharer.user_details.featured} for {self.dataSharer.jump_url} via DM")


async def handle_notify_user_interaction(bot: commands.Bot, message: discord.Message, user_details: User):
    original_comment = message.content or ''
    tmp_dir = "temp"
    os.makedirs(tmp_dir, exist_ok=True)
    file_save_path = os.path.join(tmp_dir, f"{message.id}.txt")

    dataSharer = DataSharer(comment=original_comment, file_save_path=file_save_path,
                            jump_url=message.jump_url, user_details=user_details, bot=bot)
    myView = MyView(dataSharer)

    # user = await bot.fetch_user(user_details.id)  # TODO: use author.send
    # delete after 1 hour
    # await user.send(format_msg(dataSharer), view=myView, delete_after=3600)
    await message.author.send(format_msg(dataSharer), view=myView, delete_after=3600)
