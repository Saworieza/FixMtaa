from __future__ import absolute_import

from proj.celery import app

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

def findDomainNegationKeywords(tweet_tokens, identified_domain):
    # create a new list containing only keywords from that domain
    specified_domain_negation_keywords = [text for text, domain in domain_negation_keywords_list if domain == identified_domain]
    if not specified_domain_negation_keywords:
        # this means that this is an empty list
        print "The domain doesn't have any negation keywords"
        return (tweet_tokens, False)
    token_index = 0
    for text, classifier, domain in tweet_tokens:
        # 'DI' may also be 'DNK'
        # since we have determined the domain, 'DI' keywords are not useful anymore
        if classifier == 'u' or classifier == 'DI':
            if text in specified_domain_negation_keywords:
                tweet_tokens[token_index] = (text, 'DNK', identified_domain)
        token_index = token_index + 1
    """
    -> From the list of all domain keywords, filter them and remain with the
        one that point with the selected domain.
    """
    print tweet_tokens
    return (tweet_tokens, True)  # True: The identified_domain passed as input is valid

def findNegationKeywords(tweet_tokens):
    # TODO: Figure out if general negation should also be suited for each domain
    # token_texts = [text for text, classifier, domain in tweet_tokens]
    # negation_data = [value for value, domain, is_prefixed in negation_keywords_list]
    token_index = 0
    for text, classifier, domain in tweet_tokens:
        if classifier == 'u':
            if text in negation_data:
                # update tweet_tokens
                # negation_index = negation_data.index(text)
                tweet_tokens[token_index] = (text, 'NK', 'u')
        token_index = token_index + 1
    print tweet_tokens
    return tweet_tokens

def findDomainIndicatorKeywords(tweet_tokens):
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
            # update tweet_tokens if domain keyword is present in tweet
            domain_index = domain_data.index(token)
            tweet_tokens[index] = (token, 'DK', domain_keywords_list[domain_index][1])
    print tweet_tokens
    # findDomainIndicatorKeywords(tweet_tokens=tweet_tokens)
    return tweet_tokens

"""
print domain_keywords_list
print domain_indicator_keywords_list
print negation_keywords_list
print domain_negation_keywords_list
"""

def extract_tweet_domain_information(tweet_tokens):
    return findDomainIndicatorKeywords(findDomainKeywords(tweet_tokens=tweet_tokens))

def get_tweet_domain(tweet_tokens):
    """
    -> At this point, we expect the tweet to have 'DK' and/or 'DI' tokens present
    -> If the tweet does not have both ('DK' or 'DI'), then we cannot determine the domain
       of the tweet. We need to mark it as 'domainless' and store it somewhere for
       futher analysis.
    -> If we encounter a 'DK', we stop getting the tweet domain and use the domain
       keyword provided as our identified_domain.
    -> If there are no "DK's", we rely on the "DI's" available in the tweet.
    -> For a first implementation, we will use the domain where it's "DI's" show
       up the most as the identified_domain. This only works if there are no ties
       btwn different domains.
    -> In the future, this a great place to add a regression model that can give
       us the most probable (yes, probability) domain the tweet belongs to given
       its 'DI' tokens.
    """

@app.task
def analysis_tweet_receiver(tweet, tweet_tokens):
    """
    ->  This is the method that recieves the unmodifed tweets, together with
        the tweets cleaned tokens.
    """
    # find 'DK' and 'DI' tokens in tweet
    tweet_tokens = extract_tweet_domain_information(tweet_tokens=tweet_tokens)
    # identified_domain = get_tweet_domain(tweet_tokens=tweet_tokens)
