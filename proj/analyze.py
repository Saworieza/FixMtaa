from __future__ import absolute_import

"""
Analyze the tweet and try to figure out what the user means
Before analyzing you have to clean the data
"""

# import regex
import re

# import csv read_raw_tweets_from_cassandra
import csv

# import nltk
import nltk

from proj.celery import app

import pycassa

domain_recongition_classifier = None
issue_recognition_classifier = None

domain_feature_list = []
issue_feature_list = []

# use this to extract features of a domain
def domainExtractFeatures(feature_vector):
    tweet_words = set(feature_vector)  # remove duplicate vectors from tweet
    features = {}
    for word in domain_feature_list:
        domain = None
        if word[0] in tweet_words:
            domain = word[1]  # if keyword is mentioned in tweet words, add it to as a mentioned category
        else:
            domain = 'undefined' # if it wasn't mentioned then, we put it in the undefined category
        features['domain mention (%s)' % word[0]] = domain # find out if the set contains the words in the domain feature list
    return features

def getDomainRecognitionList():
    electricity_trainer_csv = open('proj/domain_keywords.csv', "rb")
    reader = csv.reader(electricity_trainer_csv)

    domain_list = [] # tuple containing a word and its domain

    # specific for electricity
    # TODO: Switch to a more generalized csv file, that will work for new domains
    for row in reader:
        if row[0] is not None:
            domain_list.append((row[0],'electricity'))
        if row[1] is not None:
            if row[1] != "":
                domain_list.append((row[1],'water'))
        """
        colnum = 0
        for col in row:
            domain_list.append((row[colnum], 'electricity'))
        """
    print 'Domain list:'
    print domain_list
    return domain_list

def getDommainRecognitionTrainingSet():
    # TODO: Read data from domain_training_set.csv, pass it to you extractor & use that information and results to train your classifier

    training_set = []  # training set is a list of tuples (features, 'result')


# to train the naive bayes algorithm, you need a tuple:
    # (dictionary, label)

#initialize lists and classifiers in memory

domain_feature_list = getDomainRecognitionList()
domain_recongition_classifier = nltk.NaiveBayesClassifier.train()


def getIssueRecognitionList():
    pass

def getIssueRecognitionTrainingSet():
    pass

@app.task
def analyzeTweet(tweet):
    print 'about to analyze tweet'
    cleaned_tweet_text = cleanTweet(tweet_text=tweet['text'])
    feature_vector = getFeaturevector(tweet_text=cleaned_tweet_text)
    print 'Showing domain features:'
    print domainExtractFeatures(feature_vector=feature_vector)
    print 'Showing classifier output:'
    print domain_recongition_classifier.classify(domainExtractFeatures(feature_vector=feature_vector))

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
