from __future__ import absolute_import

from proj.celery import app
from proj.updated_analysis import analysisTweetReceiver

import re
import csv

# place stop words in memory to avoid re-generation
stop_words_list = []

def generate_stop_words():
    stop_words = open('proj/stopwords.csv', "rb")
    reader = csv.reader(stop_words)
    for row in reader:
        stop_words_list.append(row[0])

generate_stop_words()

@app.task
def saveRawTweetToCassandra(tweet):
    pass

def saveTweetTokensToCassandra(tweet_tokens):
    pass

def cleanTweet(tweet_text):
    # Convert to lower case
    tweet_text = tweet_text.lower()
    # Convert www.* or https?://* to URL
    tweet_text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet_text)
    # Convert @username to AT_USER
    tweet_text = re.sub('@[^\s]+','AT_USER',tweet_text)
    #Remove additional white spaces
    tweet_text = re.sub('[\s]+', ' ', tweet_text)
    #Replace #word with word
    tweet_text = re.sub(r'#([^\s]+)', r'\1', tweet_text)
    #trim
    tweet_text = tweet_text.strip('\'"')
    print 'tweet pre-processed:'
    print tweet_text
    return tweet_text


def tokenizeTweet(tweet_text):  # similar to getFeaturevector function
    tweet_text = cleanTweet(tweet_text=tweet_text)
    tweet_tokens = []
    words = tweet_text.split()
    for word in words:
        # strip out punctuation
        word = word.strip('\'"?,.')
        if word not in stop_words_list:
            tweet_tokens.append((word, 'u', 'u'))
    return tweet_tokens  # returns a list of token tuples

@app.task
def tweetReceiver(tweet_text):
    tweet_tokens = tokenizeTweet(cleanTweet(tweet_text=tweet_text))
    analysisTweetReceiver.apply_async((tweet_text,tweet_tokens))
