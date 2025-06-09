import os
import random
import requests
import tweepy
from datetime import datetime, time
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from telegram.ext import Updater, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@your_channel')
INSTAGRAM_TOKEN = os.getenv('IG_TOKEN')
IG_USER_ID = os.getenv('IG_USER_ID')  # Instagram Business User ID
TWITTER_BEARER = os.getenv('TW_BEARER')

# Hashtag lists
IG_HASHTAGS = ['امید صباغ نو','#امید_صباغ_نو','#محمدمهدی_سیار',
               'محمدمهدی سیار','#سجاد_سامانی','سجاد سامانی',
               '#حامد_ابراهیم_پور','حامد ابراهیم پور',
               '#حامد_عسکری','حامد عسکری','#مولانا','مولانا'
               ,'#حافظ','حافظ','#سعدی','سعدی','#حسین_منزوی'
               ,'حسین منزوی','#کاظم_بهمنی','کاظم بهمنی',
               '#حسین_صفا','حسین صفا','#فاضل_نظری','فاضل نظری']

TW_HASHTAGS = ['امید صباغ نو','#امید_صباغ_نو','#محمدمهدی_سیار',
               'محمدمهدی سیار','#سجاد_سامانی','سجاد سامانی',
               '#حامد_ابراهیم_پور','حامد ابراهیم پور',
               '#حامد_عسکری','حامد عسکری','#مولانا','مولانا'
               ,'#حافظ','حافظ','#سعدی','سعدی','#حسین_منزوی'
               ,'حسین منزوی','#کاظم_بهمنی','کاظم بهمنی',
               '#حسین_صفا','حسین صفا','#فاضل_نظری','فاضل نظری']

# Initialize Twitter client
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER)

# Fetch random Instagram post by hashtag
def fetch_instagram_post(hashtag):
    # Get hashtag ID
    search_url = (
        f"https://graph.facebook.com/ig_hashtag_search?" 
        f"user_id={IG_USER_ID}&q={hashtag}&access_token={INSTAGRAM_TOKEN}"
    )
    resp = requests.get(search_url).json().get('data', [])
    if not resp:
        return None
    tag_id = resp[0]['id']
    # Fetch recent media for hashtag
    media_url = (
        f"https://graph.facebook.com/{tag_id}/recent_media?" 
        f"user_id={IG_USER_ID}&fields=id,caption,media_type,media_url,permalink&access_token={INSTAGRAM_TOKEN}"
    )
    posts = requests.get(media_url).json().get('data', [])
    if not posts:
        return None
    return random.choice(posts)

# Fetch random Twitter post by hashtag
def fetch_twitter_post(hashtag):
    query = f"#{hashtag} -is:retweet lang:fa has:media"
    tweets = twitter_client.search_recent_tweets(
        query=query,
        tweet_fields=['id','text','attachments'],
        expansions=['attachments.media_keys'],
        media_fields=['url','preview_image_url','type'],
        max_results=50
    )
    if not tweets.data:
        return None
    tweet = random.choice(tweets.data)
    media = []
    if tweets.includes and 'media' in tweets.includes:
        for m in tweets.includes['media']:
            media.append({'type': m.type, 'url': m.url or m.preview_image_url})
    return {'tweet': tweet, 'media': media}

# Format and send post
def send_post(context: CallbackContext):
    bot: Bot = context.bot
    # Random choice source
    if random.random() < 0.5:
        hashtag = random.choice(IG_HASHTAGS)
        post = fetch_instagram_post(hashtag)
        if not post:
            return
        caption = post.get('caption', '')
        text = f"{caption}\n\n@hossein_safa_fan • {hashtag}"
        media_type = post.get('media_type')
        media_url = post.get('media_url')
        if media_type == 'IMAGE':
            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=media_url,
                caption=text
            )
        elif media_type == 'VIDEO':
            bot.send_video(
                chat_id=CHANNEL_ID,
                video=media_url,
                caption=text
            )
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=text)
    else:
        hashtag = random.choice(TW_HASHTAGS)
        data = fetch_twitter_post(hashtag)
        if not data:
            return
        tweet = data['tweet']
        media = data['media']
        text = f"{tweet.text}\n\n@hossein_safa_fan • {hashtag}"
        if media:
            # Prepare media list
            if len(media) == 1:
                m = media[0]
                if m['type'] == 'photo':
                    bot.send_photo(chat_id=CHANNEL_ID, photo=m['url'], caption=text)
                else:
                    bot.send_video(chat_id=CHANNEL_ID, video=m['url'], caption=text)
            else:
                input_media = []
                for m in media:
                    if m['type'] == 'photo':
                        input_media.append(InputMediaPhoto(m['url']))
                    else:
                        input_media.append(InputMediaVideo(m['url']))
                # Telegram requires caption on the first media
                input_media[0].caption = text
                bot.send_media_group(chat_id=CHANNEL_ID, media=input_media)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=text)

# Schedule three times a day
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    jq = updater.job_queue
    times = [time(hour=10, minute=0), time(hour=17, minute=0), time(hour=21, minute=0)]
    for t in times:
        jq.run_daily(send_post, time=t, days=(0,1,2,3,4,5,6))
    updater.start_polling()
    updater.idle()

if name == 'main':
    main()