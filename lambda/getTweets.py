import datetime
import tweepy
import time
from collections import OrderedDict
import boto3
import json
import itertools
from wordcloud import WordCloud, STOPWORDS
from getWordCloud import generate_word_cloud
import matplotlib.pyplot as plt

def getTweets(amount, api, tweettime):
    #Use tweepy/Twitter API in order to search for any tweets with "covid"

    tweets = {}
    #Loop for double the amount of time waiting 30 seconds each time
    for _ in range(tweettime*2):
        #call tweepy search API for english tweets
        tweetsearch = api.search(q="covid-19", count=amount, lang="en")
        #add each tweet to dictionary using retweet as key
        for tweet in tweetsearch:
            tweets[tweet.retweet_count] = [tweet.text]
        #Process and save tweet data
        tweet_list = sort_tweets(tweets, amount)
        save_to_bucket(tweet_list, 'tweets.txt')
        calculate_metrics(tweet_list)
        time.sleep(30)
        print("Tweets Collected: "+str(len(tweets)))
    
    print("Total Tweets Collected: "+str(len(tweets)))
    print(tweets)
    return tweets

def sort_tweets(tweets, amount):
    #sort tweets into an ordered dictionary by the key (retweet count), use reverse to flip list to largest-smallest
    tweets_by_date = OrderedDict(sorted(tweets.items(), key=lambda t: t[0],reverse=True))
    #Cut dictionary to desired length
    tweets_by_date = OrderedDict(itertools.islice(tweets_by_date.items(), amount))
    return tweets_by_date

def calculate_metrics(tweet_list):
    #Generate word frequency dictionary for all tweets collected
    stringlist = ""
    for tweet in tweet_list:
        #Bool instances sometimes get returned, these must be ignored
        if isinstance(tweet_list[tweet], bool):
            tweet = "N/A"
        else:
            #Add tweet to string
            tweet = str(tweet_list[tweet][0])
        stringlist += tweet+" "
    #generate wordcloud
    generate_word_cloud(stringlist,'tweets-wordcloud.png')
    #Split each word into list
    stringlist = stringlist.split()
    #Generate word frequencies
    word_frequencies = wordListToFreqDict(stringlist)
    save_to_bucket(word_frequencies,'word_frequencies.txt')


def wordListToFreqDict(wordlist):
    #Count each frequency of the split words and zip into a key value store
    wordfreq = [wordlist.count(p) for p in wordlist]
    return dict(list(zip(wordlist,wordfreq)))

def save_to_bucket(tweet_list, FILE_NAME):
    #Save tweet list to an s3 bucket
    BUCKET_NAME = "1706224-tweets"
    s3 = boto3.resource('s3')
    object = s3.Object(BUCKET_NAME, FILE_NAME)
    object.put(Body=(bytes(json.dumps(tweet_list, indent=2).encode('UTF-8'))))


    
