import discord
from discord.ext import commands
from classes import User
from utils import convert_user_to_markdown
import os

from handlers.update_details import handle_update_details

# send dm to user
# Edit comment button - opens a modal for editing comment
# Edit personal details - opens a modal for editing personal details


class DataSharer():
    def __init__(self, comment: str = "", file_save_path: str = "", jump_url: str = "", user_details: User = None):
        self.comment = comment
        self.file_save_path = file_save_path
        self.jump_url = jump_url
        self.user_details = user_details


class UpdateCommentModal(discord.ui.Modal, title='Update comment'):
    commentInput = discord.ui.TextInput(
        label='Comment', default="", style=discord.TextStyle.paragraph)

    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.dataSharer = dataSharer

        # use txt files to track whether the post comment has been edited
        # set updated comment
        if os.path.exists(self.dataSharer.file_save_path):
            with open(self.dataSharer.file_save_path, 'r') as file:
                edited_comment = file.read()
                self.commentInput.default = edited_comment
        else:
            # set original comment
            self.commentInput.default = self.dataSharer.comment

    async def on_submit(self, interaction: discord.Interaction):
        # update txt file with new comment
        with open(self.dataSharer.file_save_path, 'w') as file:
            file.write(self.commentInput.value)

        msg = f"## Your art may be featured on Banodoco's social channels today: {self.dataSharer.jump_url}\n\nYour current details are as follows:\n\n{convert_user_to_markdown(self.dataSharer.user_details)}\n**Comment:** {self.commentInput.value}\n\n_To stop yourself from being featured, use the `/update_featuring` command._"

        myView = MyView(dataSharer=self.dataSharer)

        await interaction.response.edit_message(content=msg, view=myView)


class UpdateDetailsModal(discord.ui.Modal, title='Update personal details'):
    nameInput = discord.ui.TextInput(label='Name', required=True)
    twitterInput = discord.ui.TextInput(label='Twitter', required=False)
    instagramInput = discord.ui.TextInput(label='Instagram', required=False)
    youtubeInput = discord.ui.TextInput(label='Youtube', required=False)
    websiteInput = discord.ui.TextInput(label='Website', required=False)

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
        new_user = User(id=self.dataSharer.user_details.id, name=self.nameInput.value, twitter=self.twitterInput.value,
                        instagram=self.instagramInput.value, youtube=self.youtubeInput.value, website=self.websiteInput.value, featured=self.dataSharer.user_details.featured)
        # update database with new details
        new_user_details = handle_update_details(
            new_user, interaction)
        self.dataSharer.user_details = new_user_details

        msg = f"## Your art may be featured on Banodoco's social channels today: {self.dataSharer.jump_url}\n\nYour current details are as follows:\n\n{convert_user_to_markdown(self.dataSharer.user_details)}\n**Comment:** {self.dataSharer.comment}\n\n_To stop yourself from being featured, use the `/update_featuring` command._"

        myView = MyView(dataSharer=self.dataSharer)

        await interaction.response.edit_message(content=msg, view=myView)


class MyView(discord.ui.View):
    def __init__(self, dataSharer: DataSharer):
        super().__init__()
        self.timeout = None
        self.dataSharer = dataSharer

    @discord.ui.button(label="Edit Comment", style=discord.ButtonStyle.green)
    async def open_comment_modal(self, interaction: discord.Interaction, _):
        updateCommentModal = UpdateCommentModal(self.dataSharer)
        await interaction.response.send_modal(updateCommentModal)

    @discord.ui.button(label="Edit Details", style=discord.ButtonStyle.blurple)
    async def open_details_modal(self, interaction: discord.Interaction, _):
        updateDetailsModal = UpdateDetailsModal(self.dataSharer)
        await interaction.response.send_modal(updateDetailsModal)


async def handle_notify_user_interaction(bot: commands.Bot, message: discord.Message, user_details: User):
    original_comment = message.content or ''
    tmp_dir = "temp"
    os.makedirs(tmp_dir, exist_ok=True)
    file_save_path = os.path.join(tmp_dir, f"{message.id}.txt")

    user = await bot.fetch_user(user_details.id)  # TODO: use author.send
    msg = f"## Your art may be featured on Banodoco's social channels today: {message.jump_url}\n\nYour current details are as follows:\n\n{convert_user_to_markdown(user_details)}\n**Comment:** {message.content or ''}\n\n_To stop yourself from being featured, use the `/update_featuring` command._"

    dataSharer = DataSharer(comment=original_comment, file_save_path=file_save_path,
                            jump_url=message.jump_url, user_details=user_details)
    myView = MyView(dataSharer)

    await user.send(msg, view=myView)
