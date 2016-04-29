from __future__ import absolute_import

from datetime import timedelta, datetime
import time

from celery import Task

from proj.celery import app
from celery.decorators import analyze_tweet

from proj.analyze import issue_categorization

import pycassa

# callback classes help to reduce callback hell
# we define on success an failure callbacks where the method is created, and not where it is invoked
# slice out last 3 characters digits from twitter timestamps
# python timestamps work to the second, & not to the millisecond


"""
A Cassandra table created with compact storage can only have one column that is not part of the primary key.
"""

@app.task
def save_raw_tweet_to_cassandra(tweet):
    pool = pycassa.ConnectionPool('tweets')
    cf = pycassa.ColumnFamily(pool, 'rawtweets')
    cf.insert(tweet['id_str'], {'tweet_text': tweet['text'], 'tweet_timestamp': int(tweet['timestamp_ms'][:-3]), 'user_id': tweet['user']['id_str'], 'user_name': tweet['user']['name'], 'user_screen_name': tweet['user']['screen_name'], 'user_created_at': tweet['user']['created_at']})
    # after successfully storing the tweet, send it for analysis
    issue_categorization.apply_async((tweet,))


# we won't be recieving raw tweets from Cassandra anymore
# it's quite likely we wont need this periodic task
@periodic_task(run_every=timedelta(seconds= 30))
def read_raw_tweets_from_cassandra():
    pass
