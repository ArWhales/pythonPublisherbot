import instaloader
import asyncio
from telethon.tl.types import PeerChannel
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
import os
import time
import asyncio

# Instagram username
INSTAGRAM_USERNAME = 'arabic.whales'

# Instagram password
INSTAGRAM_PASSWORD = 'ArabicWhales'

# Telegram bot token
TELEGRAM_BOT_TOKEN = '6786433267:AAGUMabEuC2buKFyC22KKW48K1j12Lp1XCA'

# Telegram group ID
TELEGRAM_GROUP_ID = '@ArabicWhales'

# Telegram channel ID
TELEGRAM_CHANNEL_ID = '@ArabicWhalesSignals'

# Telegram API
api_id = '23399628'
api_hash = '3584fea271f1c68f67bf379b73b40fa3'

# Initialize Instaloader
L = instaloader.Instaloader()

# Initialize the list to store shared post IDs
shared_post_ids = []

# Initialize a variable to store the last sent message ID
last_sent_message_id = None

# Initialize a variable to store the last forwarded message ID
last_forwarded_message_id = None

# Login to Instagram
L.context.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

# Initialize Telegram client
client = TelegramClient(StringSession(), api_id, api_hash)

# Connect to Telegram
client.start()

# Function to check if a post has been already shared
def is_post_shared(post_id):
    return post_id in shared_post_ids

# Function to fetch and forward the latest Instagram post to the Telegram group
async def fetch_and_forward_latest_instagram_post():
    global last_sent_message_id
    try:
        profile = instaloader.Profile.from_username(L.context, INSTAGRAM_USERNAME)
        posts = profile.get_posts()
        latest_post = next(posts)

        # Check if the post has been already shared
        if is_post_shared(latest_post.shortcode):
            return

        # Split the caption into paragraphs
        paragraphs = latest_post.caption.split('\n')

        # Take the first paragraph as the comment
        first_paragraph = paragraphs[0] if paragraphs else ''

        # Add a link to the Instagram post for more details
        instagram_link = f"https://www.instagram.com/p/{latest_post.shortcode}/"
        message = f"{first_paragraph}\n\nبقية التفاصيل تجدها في حسابنا على الانستقرام: {instagram_link}"

        # Download the post
        L.download_post(post=latest_post, target=INSTAGRAM_USERNAME)

        # Find the downloaded file
        filename = f"{INSTAGRAM_USERNAME}/{latest_post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg"

        # Send the photo with the caption to the Telegram group
        sent_message = await client.send_file(TELEGRAM_GROUP_ID, filename, caption=message)

        # Check if the message ID is different from the last sent message ID
        if last_sent_message_id != sent_message.id:
            last_sent_message_id = sent_message.id
            shared_post_ids.append(latest_post.shortcode)
    except Exception as e:
        print(f"Error: {e}")

# Function to forward messages from the channel to the group
async def forward_messages():
    global last_forwarded_message_id
    try:
        # Get the entity of the group and the channel
        group_entity = await client.get_entity(TELEGRAM_GROUP_ID)
        channel_entity = await client.get_entity(TELEGRAM_CHANNEL_ID)

        # Subscribe to new message events in the channel
        @client.on(events.NewMessage(chats=channel_entity))
        async def handler(event):
            # Check if the message has already been forwarded
            if event.message.forward:
                return

            # Forward the message to the group
            sent_message = await client.forward_messages(group_entity, event.message)

            # Check if the message ID is different from the last forwarded message ID
            if last_forwarded_message_id != sent_message.id:
                last_forwarded_message_id = sent_message.id
    except Exception as e:
        print(f"Error: {e}")

# Main function to run both tasks
async def main():
    while True:
        await fetch_and_forward_latest_instagram_post()
        await forward_messages()
        # Wait for 1 minute before checking for new posts again
        await asyncio.sleep(60)  # 60 seconds = 1 minute

# Run the main function
asyncio.get_event_loop().run_until_complete(main())
