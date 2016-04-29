from __future__ import absolute_import

"""
Analyze the tweet and try to figure out what the user means
Before analyzing you have to clean the data
"""

# import regex
import re

# import nltk
import nltk

from proj.celery import app

import pycassa

@app.task
def analyzeTweet(tweet):
    print 'about to analyze tweet'
    cleaned_tweet_text = cleanTweet(tweet_text=tweet['text'])
    feature_vector = getFeaturevector(tweet_text=cleaned_tweet_text)
    print feature_vector

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

    # look for 2 or more repetitions of character and replace with the character itself
def replaceTwoOrMore(word):
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", word)

def getFeaturevector(tweet_text):
    feature_vector = []
    words = tweet_text.split()
    for word in words:
        word = replaceTwoOrMore(word=word)
        # strip out punctuation
        word = word.strip('\'"?,.')
        # check if the word stats with an alphabet
        # TODO: find out if this works for Swahili
        # val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", word)
        # TODO: Add list of stop words that don't add meaning to the feature vector
        feature_vector.append(word.lower())
    return feature_vector

    # finds out whether this is a water or electricty issue
def issueCategorization():
    pass

    # finds out what time the issue occured
def issueTimeCategorization():
    pass

    # finds out where this issue occured
def issuePlaceRecognition():
    pass

    # finds out where/who to direct the issue to
def organizationMatcher():
    pass
