import discord


class MessageWithReactionCount():
    def __init__(self, message: discord.Message, unique_reactions_count: int):
        self.message = message
        self.unique_reactions_count = unique_reactions_count


class User():
    def __init__(self, id: int, name: str, youtube_username: str, twitter_username: str, instagram_username: str, website_url: str, featured: bool):
        self.id = id
        self.name = name
        self.youtube_username = youtube_username
        self.twitter_username = twitter_username
        self.instagram_username = instagram_username
        self.website_url = website_url
        self.featured = featured

    # for overriding atributes
    def set_attribute(self, attribute: str, value):
        setattr(self, attribute, value)
