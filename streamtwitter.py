from __future__ import absolute_import

"""
Here is where we connect to twitter
Twitter credentials are set up in environment variables, for extra security and convenience
"""

import os
import json

from twitter import OAuth, TwitterHTTPError, TwitterStream

# get auth credentials from environment variables
CONSUMER_KEY = os.environ.get('TWITTER_API_KEY')
CONSUMER_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

# give credentials to auth library
oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

twitter_stream = TwitterStream(auth=oauth, block=False)

# twitter_stream creates an iterator that we can use to read tweets from the stream
iterator = twitter_stream.statuses.filter(track="#fixMtaa")

# read all tweets in the iterator
for tweet in iterator:
    if tweet is not None:
        print tweet
