import json
import os
import tweepy
from getTopics import getTopics
from getTweets import getTweets
import boto3    

def clear_bucket():
    BUCKET_NAME = "1706224-tweets"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.objects.all().delete()
    
    
def lambda_handler(event, context):
    

    #Get Twitter API keys from Enviroment Variables 
    api_key = os.environ['APIKEY']
    api_secret = os.environ['APISECRET']
    bearer_token = os.environ['BEARERTOKEN']
    access_token = os.environ['ACCESSTOKEN']
    access_token_secret = os.environ['ACCESSSECRET']
    
    
    #Set up tweepy handler using api key and secret
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    
    #Get variables from lambda event
    function = event['function']
    amount = event['amount']
    _time = event['time']
    

    #clear_bucket()
    #Run lamdbda functions based on event variables
    if function == "tweets":
        tweets = getTweets(amount, api, _time)
    if function == "topics":
        topics = getTopics(amount, api)

    

    