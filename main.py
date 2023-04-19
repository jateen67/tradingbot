import datetime
import tweepy
import os
import time
import io
import hashlib
import hmac
import requests
import urllib.request
import urllib.parse
from dotenv import load_dotenv, find_dotenv
from google.cloud import vision
from google.cloud import vision_v1

load_dotenv(find_dotenv())

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_SECRET_TOKEN = os.getenv('TWITTER_SECRET_TOKEN')
TOTAL_AMOUNT = os.getenv('TOTAL_AMOUNT')
MAX_AMOUNT = os.getenv('MAX_AMOUNT')

tweepy_auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
tweepy_auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_SECRET_TOKEN)
tweepy_api = tweepy.API(tweepy_auth)

tweet_dates = open("tweet_dates.txt", 'r').read().split('\n')
dates = []


def has_dog_ticker(s):
    for i in range(len(s)):
        if s[i: i + 3].lower() == 'dog':
            for j in range(i + 1):
                if s[i - j - 1] == '@':
                    break
                elif i - j == 0 or s[i - j - 1] == ' ':
                    return True

    return False


def has_dog_image(tweet):

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv(
        'GOOGLE_APPLICATION_CREDENTIALS')

    client = vision.ImageAnnotatorClient()

    try:
        media_url = ((tweet.entities)['media'])[0]['media_url']
    except Exception:
        return False

    with urllib.request.urlopen(media_url) as url:
        with open('image.jpg', 'wb') as img:
            img.write(url.read())

    with io.open('image.jpg', 'rb') as img:
        content = img.read()

    image = vision_v1.types.Image(content=content)

    res = client.text_detection(image=image)
    for e in res.text_annotations:
        if has_dog_ticker(e.description):
            return True

    res = client.label_detection(image=image)
    for e in res.label_annotations:
        if has_dog_ticker(e.description):
            return True

    res = client.object_localization(image=image)
    for e in res.localized_object_annotations:
        if has_dog_ticker(e.name):
            return True

    return False


def validate_time(s):

    date = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    current_year = datetime.datetime.now().year

    if date.year < current_year:
        return False
    elif date.month == 1 and date.day < 15:
        return False
    else:
        return True


def trade(symbol, side, quantity):

    params = {
        'symbol': symbol,
        'side': side,
        'positionSide': 'LONG',
        'type': 'MARKET',
        'quantity': int(quantity),
        'timestamp': int(time.time() * 1000)
    }

    params['signature'] = hmac.new(BINANCE_SECRET_KEY.encode(
        'utf-8'), urllib.parse.urlencode(params).encode('utf-8'), hashlib.sha256).hexdigest()

    r = requests.post('https://dapi.binance.com/dapi/v1/order',
                      headers={
                          'X-MBX-APIKEY': BINANCE_API_KEY
                      }, params=params)

    print('request made:\n'+str(r.json()))


def main():

    while True:
        time.sleep(1)

        try:
            elon_tweet = tweepy_api.user_timeline(
                screen_name='elonmusk', count=1)
        except Exception:
            continue

        for e in elon_tweet:
            text = e.text
            created_at = e.created_at

            if validate_time(str(created_at)) and not str(created_at) in tweet_dates and not created_at in dates:
                if has_dog_ticker(text) or has_dog_image(e):

                    balance = TOTAL_AMOUNT

                    while balance != 0:
                        if balance > MAX_AMOUNT:
                            trade('DOGEUSD_PERP', 'BUY', MAX_AMOUNT)
                            balance -= MAX_AMOUNT
                        else:
                            trade('DOGEUSD_PERP', 'BUY', balance)
                            balance = 0

                    time.sleep(3600)
                    balance = TOTAL_AMOUNT

                    while balance != 0:
                        if balance > MAX_AMOUNT:
                            trade('DOGEUSD_PERP', 'SELL', MAX_AMOUNT)
                            balance -= MAX_AMOUNT
                        else:
                            trade('DOGEUSD_PERP', 'SELL', balance)
                            balance = 0

                open("tweet_dates.txt", 'a').write("\n"+str(created_at))
                dates.append(created_at)


main()
