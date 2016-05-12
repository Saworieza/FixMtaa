from __future__ import absolute_import

from proj.celery import app
from proj.updated_analysis import analysisTweetReceiver

import re
import csv

from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra import util
cluster = Cluster(['127.0.0.1'])  # use default args for now

session = cluster.connect('tweets')
# session = cluster.connect()  # avoid assuming use of a particular keyspace

# list of prepared statements
save_raw_tweet_st = session.prepare("""INSERT INTO raw_tweets_tweet_id (tweet_id, tweet_timestamp, tweet_text, user_screen_name, user_location, is_geo_tagged) VALUES (?, ?, ?, ?, ?, ?) """)
save_raw_tweet_st.consistency_level = ConsistencyLevel.ONE

# place stop words in memory to avoid re-generation
stop_words_list = []

def generate_stop_words():
    stop_words = open('proj/stopwords.csv', "rb")
    reader = csv.reader(stop_words)
    for row in reader:
        stop_words_list.append(row[0])

generate_stop_words()

@app.task
def saveRawTweetToCassandraByTweetId(tweet):
    # TODO: Choose between saving tweet id as a number or a string [Right now its a string]
    """
    Store by tweet_id and order by timestamp
    || tweet_id | tweet_timestamp || tweet_text | user_screen_name | user_location | is_geo_tagged |
    """
    print 'saving raw tweet to cassandra'
    print 'another code check'
    geo_tagged = None
    if tweet['geo'] == None:
        geo_tagged = False
    else:
        geo_tagged = True
    # tweet_t_stamp = util.datetime_from_timestamp(int(tweet['timestamp_ms'][:-3])) # remove milliseconds from timestamp
    session.execute(save_raw_tweet_st, (tweet['id_str'], int(tweet['timestamp_ms'][:-3]), tweet['text'], tweet['user']['screen_name'], tweet['user']['location'], geo_tagged), timeout=2000, trace=True)
    # future = session.execute_async("INSERT INTO raw_tweets_tweet_id (tweet_id, tweet_timestamp, tweet_text, user_screen_name, user_location, is_geo_tagged) VALUES (%s, %s, %s, %s, %s, %s)", (tweet['id_str'], int(tweet['timestamp_ms'][:-3]), tweet['text'], tweet['user']['screen_name'], tweet['user']['location'], geo_tagged))
    # print future
    # future.result()
    print 'raw tweet saved to cassandra'


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
    # print 'tweet pre-processed:'
    # print tweet_text
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
def tweetReceiver(tweet):
    # TODO: Ignore retweets for now, but you can store retweets for a tweet in a cassandra counter value, to give it more priority
    # TODO: Ignore tweet replies for now, but we can store them in cassandra for futher analysis
    print 'tweet received'
    if tweet.get('retweeted_status') is not None:
        print 'ignoring retweet'
        return
    if tweet['in_reply_to_status_id_str'] is not None:
        print 'ignoring replied tweet'
        return
    print 'tweet passed standard checks'
    saveRawTweetToCassandraByTweetId(tweet=tweet)
    print 'finished saving tweet'
    tweet_tokens = tokenizeTweet(cleanTweet(tweet_text=tweet['text']))
    analysisTweetReceiver.apply_async((tweet, tweet['text'], tweet_tokens))
