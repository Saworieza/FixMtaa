from __future__ import absolute_import

# from proj.celery import app

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
        # word | domain | can_prefix | can_suffix
        domain_negation_keywords_list.append((row[0], row[1], row[2], row[3]))

generateDomainKeywords()
generateDomainIndicatorKeywords()
generateNegationKeywords()
generateDomainNegationKeywords()

def findDomainNegationKeywords(tweet_tokens, identified_domain):
    # create a new list containing only keywords from that domain
    specified_domain_negation_keywords = [text for text, domain, can_prefix, can_suffix in domain_negation_keywords_list if domain == identified_domain]
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

# tweet domain retriever functions below

def getDomainByDomainKeywords(tweet_tokens):
    for text, classifier, domain in tweet_tokens:
        if classifier == 'DK':
            return domain
    return None

def getDomainByDomainIdentifiers(tweet_tokens):
    domain_counter = {}
    for text, classifier, domain in tweet_tokens:
        if classifier == 'DI':
            if domain not in domain_counter:
                domain_counter[domain] = 1
            else:
                domain_counter[domain] = domain_counter[domain] + 1
    print domain_counter
    if not domain_counter:
        # empty dictionary means that no domains matched
        return None
    else:
        # TODO: Deal with max having two or more domains i.e {'electricity': 2, 'water': 2} !!!IMPORTANT!!!
        return max(domain_counter, key=domain_counter.get())

def getTweetDomain(tweet_tokens):
    """
    -> At this point, we expect the tweet to have 'DK' and/or 'DI' tokens present
    -> If the tweet does not have both ('DK' or 'DI'), then we cannot determine the domain
       of the tweet. We need to mark it as 'domainless' and store it somewhere for
       futher analysis. There could be something we missed out on.
    -> If we encounter a 'DK', we stop getting the tweet domain and use the domain
       keyword provided as our identified_domain.
    -> If there are no "DK's", we rely on the "DI's" available in the tweet.
    -> For a first implementation, we will use the domain where it's "DI's" show
       up the most as the identified_domain. This only works if there are no ties
       btwn different domains.
    -> In the future, this a great place to add a regression model that can give
       us the most probable (yes, probability) domain the tweet belongs to given
       its 'DI' tokens.
    -> All domain getter functions are defined outside this function so that we
       create a pluggable system, on that we can remove any of those functions without
       affecting the other functions. this means that they mutate state, they take in
       input and give out an output.
    -> This pluggability also allows us to add more domian getter function in the future
    """
    identified_domain = None
    identified_domain = getDomainByDomainKeywords(tweet_tokens=tweet_tokens)
    # if we find the domain by domain keywords, our search ends
    if identified_domain is not None:
        return identified_domain
    identified_domain = getDomainByDomainIdentifiers(tweet_tokens=tweet_tokens)
    return identified_domain  # will be None if the second domain getting step failed

def getKeywordsAfterNK(tweet_tokens, domain_negators):
    # TODO: Fix index not found scenario
    token_index = 0
    for text, classifier, domain in tweet_tokens:
        if classifier == 'NK':
            # check if next token classifier is a keyword
            if tweet_tokens[token_index + 1][1] == 'DK':
                # check if token classifier after keywords is a domain negator
                if tweet_tokens[token_index + 2][1] == 'DNK':
                    # if it is a domain negator, check whther it can be suffixed after a keyword
                    domain_text_to_search = tweet_tokens[token_index + 2][0]
                    dnk_index = [index for index, domain_list in enumerate(domain_negators) if domain_list[0] == domain_text_to_search]
                    if domain_negators[dnk_index][3] == 'yes':
                        return (False, 'verified')
                    else:
                        return (True, 'verified')
                else:
                    # if no domain negator comes after a keyword in this case, we have a negative tweet
                    return (True, 'verified')
        token_index = token_index + 1
    # return False & unverified if we were not able to determine sentiment after this step
    return (False, 'unverified')

def getDomainNegativeDescriptors(tweet_tokens, domain_negators):
    # TODO: Fix index not found scenario
    # 'power blackout': We can still determine 'blackout' negativity without 'power'
    token_index = 0
    for text, classifier, domain in tweet_tokens:
        if classifier == 'DNK':
            dnk_index = [index for index, domain_list in enumerate(domain_negators) if domain_list[0] == text]
            # check if if the DNK cannot be prefixed or suffixed
            if domain_negators[dnk_index][2] == 'no' and domain_negators[dnk_index][3] == 'no':
                # check if a negative keyword comes before it
                if tweet_tokens[token_index - 1][1] == 'NK':
                    return (False, 'verified')
                else:
                    return (True, 'verified')
            # check if the DNK can be prefixed before a keyword
            if domain_negators[dnk_index][2] == 'yes':
                # check if a keyword comes after it
                if tweet_tokens[token_index + 1][1] == 'DK':
                    # check if negation keyword comes before it
                    if tweet_tokens[token_index - 1][1] == 'NK':
                        return (False, 'verified')
                    else:
                        return (True, 'verified')
            # check if DNK can be suffixed after a keyword
            if domain_negators[dnk_index][3] == 'yes':
                # check if a keyword comes before it
                if tweet_tokens[token_index - 1][1] == 'DK':
                    # check if a negation keyword comes before the domain keyword
                    if tweet_tokens[token_index - 2][1] == 'NK':
                        return (False, 'verified')
                    else:
                        return (True, 'verified')
    return (False, 'unverified')

def getTweetProblem(tweet_tokens, identified_domain):
    """
    -> The model is simple enough to use if else's for now. But if we determined
       that we have undeffited, we may have to switch to decision trees if using
       if-else statements becomes cumbersome and difficult to follow.
    """
    negative_sentiment = (False, 'unverified')
    # get domain_negators for identified_domain
    domain_negators = [domain_list for index, domain_list in enumerate(domain_negation_keywords_list) if domain_list[0] == identified_domain]
    print 'filtered domain negators'
    print domain_negators
    negative_sentiment = getKeywordsAfterNK(tweet_tokens=tweet_tokens, domain_negators=domain_negators)
    if negative_sentiment[0] == False and negative_sentiment[1] == 'unverified':
        negative_sentiment = getDomainNegativeDescriptors(tweet_tokens=tweet_tokens, domain_negators=domain_negators)
    return negative_sentiment

def domainlessHandler(tweet, tweet_tokens):
    # save to cassandra & return appropriate error message to the user
    print 'implemt domainlessHandler handler function'

def positiveSentimentHandler(tweet, tweet_tokens):
    pass

def unverifiedSentimentHandler(tweet, tweet_tokens):
    pass

def extractTweetDomainInformation(tweet_tokens):
    return findDomainIndicatorKeywords(findDomainKeywords(tweet_tokens=tweet_tokens))

def extractTweetInfomationAfterDomainIdentification(tweet_tokens, identified_domain):
    return findDomainNegationKeywords(findDomainNegationKeywords(tweet_tokens=tweet_tokens), identified_domain=identified_domain)

# @app.task
def analysisTweetReceiver(tweet, tweet_tokens):
    """
    ->  This is the method that recieves the unmodifed tweets, together with
        the tweets cleaned tokens.
    """
    # find 'DK' and 'DI' tokens in tweet
    tweet_tokens = extractTweetDomainInformation(tweet_tokens=tweet_tokens)
    identified_domain = getTweetDomain(tweet_tokens=tweet_tokens)
    if identified_domain is None:
        domainlessHandler(tweet=tweet, tweet_tokens=tweet_tokens)
        return
    # update tweet tokens after domain identification
    tweet_tokens = extractTweetInfomationAfterDomainIdentification(tweet_tokens=tweet_tokens, identified_domain=identified_domain)
    # we can now use the updated tweet_tokens to identify the problem in the tweet
    # negative_sentiment is a tuple with a boolean for sentiment state and whether the boolean value has been verified by the algorithm
    # this covers the case where we don't have a negative sentiment that has been determined by the algorithm
    negative_sentiment = getTweetProblem(tweet_tokens=tweet_tokens, identified_domain=identified_domain)


# TODO: Switch to datastax python driver for cassandra
