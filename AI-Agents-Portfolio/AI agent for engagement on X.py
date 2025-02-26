# Need to first Create and apply to get the API Keys for Elevated Access (Essential Access won’t let you post tweets).
# Install dependencies & create .env file

import tweepy
import openai
import os
import time
from dotenv import load_dotenv

# Load API Keys from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# OpenAI setup
openai.api_key = OPENAI_API_KEY

def generate_tweet():
    """Generate a tweet using OpenAI"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Generate a tweet about Web3, AI, or decentralization in my style."}]
    )
    return response["choices"][0]["message"]["content"]

def like_and_reply():
    """Like and reply to relevant tweets"""
    tweets = api.search_tweets(q="Web3 OR AI OR blockchain", count=5, lang="en", result_type="recent")
    for tweet in tweets:
        try:
            api.create_favorite(tweet.id)  # Like the tweet
            reply_text = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Write a short, engaging reply to this tweet: {tweet.text}"}]
            )["choices"][0]["message"]["content"]
            api.update_status(f"@{tweet.user.screen_name} {reply_text}", in_reply_to_status_id=tweet.id)
            print(f"Replied to @{tweet.user.screen_name}")
            time.sleep(10)  # Avoid rate limits
        except tweepy.TweepError as e:
            print("Error:", e)

def tweet_something():
    """Post a tweet"""
    tweet = generate_tweet()
    api.update_status(tweet)
    print(f"Tweeted: {tweet}")

# Run actions
tweet_something()
like_and_reply()
