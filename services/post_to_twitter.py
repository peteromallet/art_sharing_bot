from shared.models import SocialMediaPost
from shared.utils import download_file
import os
from dotenv import load_dotenv
import tweepy
import asyncio

load_dotenv()

CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# https://github.com/peteromallet/art_sharing_bot/blob/main/bot.py


async def post_to_twitter(social_media_post: SocialMediaPost) -> None:
    file_save_path = os.path.join(
        'temp', social_media_post.attachment_name)
    await download_file(social_media_post.attachment_url, file_save_path)

    file_extension = os.path.splitext(social_media_post.attachment_name)[1]

    # Initialize Tweepy for v1.1 API
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    loop = asyncio.get_event_loop()

    # Upload the media file using v1.1 API in a separate thread
    if file_extension == '.gif':
        media = await loop.run_in_executor(None,
                                           lambda: api_v1.media_upload(file_save_path, chunked=True, media_category="tweet_gif"))  # use chunking
    else:
        media = await loop.run_in_executor(None,
                                           lambda: api_v1.media_upload(file_save_path))

    media_id = media.media_id_string
    print(f"Media ID: {media_id}")

    # Initialize Tweepy for v2 API
    client = tweepy.Client(consumer_key=CONSUMER_KEY,
                           consumer_secret=CONSUMER_SECRET,
                           access_token=ACCESS_TOKEN,
                           access_token_secret=ACCESS_TOKEN_SECRET)

    # Create a tweet with the media using v2 API in a separate thread
    await loop.run_in_executor(
        None, lambda: client.create_tweet(text=social_media_post.caption, media_ids=[media_id]))

    # TODO: delete at top level, if applicable
    # Delete the file after posting
    os.remove(file_save_path)
