from __future__ import absolute_import

from proj.celery import app

import pycassa


@app.task
def analyze_tweet(tweet):
    print 'about to tokenize tweet'
    print tweet
