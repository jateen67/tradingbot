# Twitter Crypto Trading Bot

This bot trades Dogecoin using the Binance API. 

It works by running a script that constantly requests information about Elon Musk's lastest tweet with the Twitter API, then analyzing it to see if there is any dog-related content in the tweet using the Google Vision API (e.g. the word "dog" in the tweet, there is a picture of a dog attached to the tweet, etc.).

If dog-related content is recognized in the tweet, the bot places an aggressive Dogecoin buy, and sells it shortly after. 
