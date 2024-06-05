import discord


class MessageWithReactionCount():
    def __init__(self, message: discord.Message, unique_reactions_count: int):
        self.message = message
        self.unique_reactions_count = unique_reactions_count


class User():
    def __init__(self, id: int, name: str, youtube: str, twitter: str, instagram: str, website: str, featured: bool):
        self.id = id
        self.name = name
        self.youtube = youtube
        self.twitter = twitter
        self.instagram = instagram
        self.website = website
        self.featured = featured

    # for overriding atributes
    def set_attribute(self, attribute: str, value):
        setattr(self, attribute, value)
