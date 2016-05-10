from __future__ import absolute_import

import csv

domain_keywords_list = []
domain_indicator_keywords_list = []
negation_keywords_list = []
domain_negation_keywords_list = []

def generateDomainKeywords():
    """
    ->  Domain keywords are those words that strongly point to a certain
        domain.
    ->  These keywords, when followed by a domain negation keyword, leads to
        to a negative sentiment about the domain.
    """
    domain_keywords = open('proj/domain_keywords_updated.csv', "rb")
    reader = csv.reader(domain_keywords)
    for row in reader:
        domain_keywords_list.append((row[0], row[1]))

def generateDomainIndicatorKeywords():
    """
    ->  Domain indicator keywords are words that point to a certain domain.
    ->  When a domain indicator is followed by a domain negation keyword, there's
        a strong chance that it isn't a negative sentiment.
    """
    domain_indicators = open('proj/indicator_keywords.csv', "rb")
    reader = csv.reader(domain_indicators)
    for row in reader:
        domain_indicator_keywords_list.append((row[0], row[1]))

def generateNegationKeywords():
    """
    ->  These are general English words that lead to negation.
    ->  If the come immediately after a domain keyword, we can strongly believe
        that a negative sentiment is insinuated, even without there being a negative
        domain keyword.
    ->  These keywords can however also negate a domain negation keyword, where
        the double negation causes a positive sentiment.
    """
    negation_keywords = open('proj/general_negation_keywords.csv', "rb")
    reader = csv.reader(negation_keywords)
    for row in reader:
        negation_keywords_list.append(row[0])

def generateDomainNegationKeywords():
    """
    -> Has been explained if you read the above comments
    """
    domain_negation_keywords = open('proj/domain_negation_keywords.csv', "rb")
    reader = csv.reader(domain_negation_keywords)
    for row in reader:
        domain_negation_keywords_list.append((row[0], row[1], row[2]))

generateDomainKeywords()
generateDomainIndicatorKeywords()
generateNegationKeywords()
generateDomainNegationKeywords()

def findDomainIndicatorKeywords(tweet_tokens, all_token_texts):
    # all_token_texts used to maintain original token index
    # no need to re-classify domain keywords
    domain_indicator_data = [value for value, domain in domain_indicator_keywords_list]
    token_index = 0
    # for simplicity's sake, we can't enumerate here
    for text, classifier, domain in tweet_tokens:
        if classifier == 'u':
            if text in domain_indicator_data:
                domain_indicator_index = domain_indicator_data.index(text)
                tweet_tokens[token_index] = (text, 'DI', domain_indicator_keywords_list[domain_indicator_index][1])
        token_index = token_index + 1
    # token_texts = [text for text, classifier, domain in tweet_tokens if classifier == 'u']
    # for index, token in enumerate(token_texts):
    print tweet_tokens
    return tweet_tokens

def findDomainKeywords(tweet_tokens):
    # get lists without meta-data
    token_texts = [text for text, classifier, domain in tweet_tokens]
    domain_data = [value for value, domain in domain_keywords_list]
    for index, token in enumerate(token_texts):
        print index
        if token in domain_data:
            # update the tweet_tokens if domain keyword is present in tweet
            domain_index = domain_data.index(token)
            tweet_tokens[index] = (token, 'DK', domain_keywords_list[domain_index][1])
    print tweet_tokens
    findDomainIndicatorKeywords(tweet_tokens=tweet_tokens, all_token_texts=token_texts)
    # return tweet_tokens

findDomainKeywords(tweet_tokens = [('water','u','u'), ('power','u','u'), ('pothole','u','u'), ('kplc','u','u')])



def findNegationKeywords(tweet_tokens):
    return tweet_tokens

def findDomainNegationKeywords(tweet_tokens):
    """
    -> From the list of all domain keywords, filter them and remain with the
        one that point with the selected domain.
    """
    return tweet_tokens

"""
print domain_keywords_list
print domain_indicator_keywords_list
print negation_keywords_list
print domain_negation_keywords_list
"""
