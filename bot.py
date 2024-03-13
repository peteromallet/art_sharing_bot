import discord
import aiohttp  # For making asynchronous HTTP requests
import tweepy
import asyncio
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
    media = await loop.run_in_executor(None, lambda: api_v1.media_upload(file_path))
    media_id = media.media_id_string

    # Initialize Tweepy for v2 API
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY, 
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN, 
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    # Create a tweet with the media using v2 API in a separate thread
    response = await loop.run_in_executor(None, lambda: client.create_tweet(
        text=text,
        media_ids=[media_id]
    ))

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
  file_path = 'user_details.csv'
  if os.path.exists(file_path):
    df = pd.read_csv(file_path)
  else:
    df = pd.DataFrame(columns=['name', 'display_name', 'block'])

  if username in df['name'].values:
    # Update existing row
    if display_name is not None:
      df.loc[df['name'] == username, 'display_name'] = display_name
    if block is not None:
      df.loc[df['name'] == username, 'block'] = block
  else:
    # Append new row using pd.concat
    new_row = pd.DataFrame([{
        'name': username,
        'display_name': display_name if display_name else '',
        'block': block if block is not None else False
    }])
    df = pd.concat([df, new_row], ignore_index=True)

  df.to_csv(file_path, index=False)


@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        username = str(message.author)
        content = message.content.strip().lower()

        # Check if the message is to block the user
        if content == "block":
            await update_user_details(username, block=True)
            await message.channel.send("You have been blocked.")

        # Check if the message is to unblock the user
        elif content == "unblock":
            await update_user_details(username, block=False)
            await message.channel.send("You have been unblocked.")

        # Update display name if the message is not a block/unblock command
        else:            
            message.content = message.content.strip()
            await update_user_details(username, display_name=message.content)
            await message.channel.send(f"Your name has been updated to '{message.content}'.")

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
            print(f"A post in #art_sharing has received more than 10 reactions from distinct users: {message.content}")

            # Download the first video attachment
            if message.attachments:
                attachment = message.attachments[0]
                # if the message contains #nt, don't tweet it
                if '#nt' not in message.content:
                    if attachment.filename.lower().endswith(('.mp4', '.mov', '.wmv', '.avi', '.gif', '.webm', '.mkv')):
                        media_folder = 'media'
                        if not os.path.exists(media_folder):
                            os.makedirs(media_folder)
                        file_path = os.path.join(media_folder, attachment.filename)
                        await download_file(attachment.url, file_path)
                        
                        # Query the CSV for the author's display name and block status
                        df = pd.read_csv('user_details.csv')
                        author_name = message.author.global_name
                        query_result = df[df['name'] == author_name]
                        if not query_result.empty:
                            # Convert to string and compare or directly compare as Boolean
                            is_blocked = query_result['block'].values[0] in ['True', True]
                            if is_blocked:
                                print(f"User {author_name} is blocked from posting.")
                                return  # Stop execution if the user is blocked
                            
                            author_display_name = query_result['display_name'].values[0] if 'display_name' in query_result and query_result['display_name'].values[0] else author_name
                            await post_tweet_with_media(f"Created by {author_display_name}:", file_path)
                        else:
                            await post_tweet_with_media(f"Created by {author_name}:", file_path)
                else:
                    print(f"Message contains #nt: {message.content}")
                                
        else:
            print(f"This post has received {len(unique_users)} reactions from distinct users: {message.content}")



client.run(DISCORD_BOT_TOKEN)  # Use the bot token from