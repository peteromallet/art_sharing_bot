import discord
import aiohttp  # For making asynchronous HTTP requests
import tweepy
import asyncio
from replit import db
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Environment variables for API keys and tokens
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True  # Needed to track members who reacted

client = discord.Client(intents=intents)


async def post_tweet_with_media(text, file_path):
  # Initialize Tweepy for v1.1 API
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api_v1 = tweepy.API(auth)

  loop = asyncio.get_event_loop()

  # Upload the media file using v1.1 API in a separate thread
  media = await loop.run_in_executor(None,
                                     lambda: api_v1.media_upload(file_path))
  media_id = media.media_id_string

  # Initialize Tweepy for v2 API
  client = tweepy.Client(consumer_key=CONSUMER_KEY,
                         consumer_secret=CONSUMER_SECRET,
                         access_token=ACCESS_TOKEN,
                         access_token_secret=ACCESS_TOKEN_SECRET)

  # Create a tweet with the media using v2 API in a separate thread
  response = await loop.run_in_executor(
      None, lambda: client.create_tweet(text=text, media_ids=[media_id]))

  # Delete the file after posting
  os.remove(file_path)

  return response


async def download_file(url, filename):
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status == 200:
        with open(filename, 'wb') as f:
          f.write(await resp.read())


async def update_user_details(username, display_name=None, block=None):
  user_key = f"user:{username}"  # Prefixing with user: to distinguish these keys
  if user_key in db.keys():
    user_details = db[user_key]
  else:
    user_details = {"name": username, "display_name": "", "block": False}

  if display_name is not None:
    user_details["display_name"] = display_name
  if block is not None:
    user_details["block"] = block

  db[user_key] = user_details


@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        username = str(message.author)
        content = message.content.strip().lower()

        # Special handling for @peteromallet
        if username.endswith('#peteromallet'):  # Adjust according to the actual discriminator of @peteromallet
            # Check if the message follows the username|display_name pattern
            if '|' in content:
                parts = content.split('|')
                if len(parts) == 2:
                    parsed_username, parsed_display_name = parts
                    await update_user_details(parsed_username.strip(), display_name=parsed_display_name.strip())
                    await message.channel.send(f"Display name for {parsed_username} updated to '{parsed_display_name}'.")
                    return  # Stop further processing

        # Regular handling for block/unblock and display name update
        if content == "block":
            await update_user_details(username, block=True)
            await message.channel.send("You have been blocked.")
        elif content == "unblock":
            await update_user_details(username, block=False)
            await message.channel.send("You have been unblocked.")
        else:
            await update_user_details(username, display_name=content)
            await message.channel.send(f"Your name has been updated to '{content}'.")


@client.event
async def on_ready():
  print(f'Logged in as {client.user}')


@client.event
async def on_raw_reaction_add(payload):
  channel = await client.fetch_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)
  user = await client.fetch_user(payload.user_id)
  print(f'{user} reacted with {payload.emoji} in {channel.name} on {message}')

  if channel.name == 'art_sharing':
    unique_users = set()

    for reaction in message.reactions:
      async for user in reaction.users():
        unique_users.add(user.id)

    if len(unique_users) == 10:
      print(
          f"A post in #art_sharing has received more than 10 reactions from distinct users: {message.content}"
      )

      # Download the first video attachment
      if message.attachments:
        attachment = message.attachments[0]
        # if the message contains #nt, don't tweet it
        if '#nt' not in message.content:
          if attachment.filename.lower().endswith(
              ('.mp4', '.mov', '.wmv', '.avi', '.gif', '.webm', '.mkv')):
            media_folder = 'media'
            if not os.path.exists(media_folder):
              os.makedirs(media_folder)
            file_path = os.path.join(media_folder, attachment.filename)
            await download_file(attachment.url, file_path)

            # Use Replit Database to query the author's display name and block status
            user_key = f"user:{message.author.name}"  # Adjust as necessary for your key naming scheme
            if user_key in db.keys():
              user_details = db[user_key]
              is_blocked = user_details.get("block", False)
              if is_blocked:
                print(f"User {message.author.name} is blocked from posting.")
                return  # Stop execution if the user is blocked

              author_display_name = user_details.get("display_name",
                                                     message.author.name)
              await post_tweet_with_media(f"Created by {author_display_name}:",
                                          file_path)
            else:
              # If no user details are found, proceed with the author's name
              await post_tweet_with_media(f"Created by {message.author.name}:",
                                          file_path)
        else:
          print(f"Message contains #nt: {message.content}")
    else:
      print(
          f"This post has received {len(unique_users)} reactions from distinct users: {message.content}"
      )


client.run(DISCORD_BOT_TOKEN)  # Use the bot token from
