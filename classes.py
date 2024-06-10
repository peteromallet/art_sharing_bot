import discord


class MessageWithReactionCount():
    def __init__(self, message: discord.Message, unique_reactions_count: int):
        self.message = message
        self.unique_reactions_count = unique_reactions_count
