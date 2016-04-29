from __future__ import absolute_import

"""
Analyze the tweet and try to figure out what the user means
"""

from proj.celery import app

import pycassa

@app.task
def analyze_tweet(tweet):
    print 'about to analyze tweet'
    clean_tweets(tweet=tweet)

def clean_tweets(tweet):
    pass

def issue_categorization():
    pass

def issue_time_categorization():
    pass

def issue_entity_recognition():
    pass

def organization_matcher():
    pass
