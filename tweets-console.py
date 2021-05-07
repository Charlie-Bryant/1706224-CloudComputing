import argparse
import sys
import time
import wordcloud
import boto3
import json
from os import system, name
from threading import Thread

def clearwindow():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux
    else:
        _ = system('clear')

def call_lambda_thread(payload, function_name):
    #Create new thread that will trigger lambda function
    t = Thread(target=trigger_lambda, args = (payload,LAMBDA_FUNCTION_NAME))
    t.daemon = False
    t.start()

def trigger_lambda(payload, function_name):
    #Invoke Lambda function using boto3
    result = client.invoke(FunctionName=function_name,
    InvocationType='RequestResponse',                                      
    Payload=json.dumps(payload))
    print(result)

def read_bucket(filename):
    #Read contents of the bucket + filename and return content
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_session_token=session)
    content_object = s3.Object('1706224-tweets', filename)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content

def parse_tweets(tweets):
    #Loop through tweet json content and print results
    for tweet in tweets:
        print("------------------------------------------------------------")
        print("Retweet Count: " + tweet)
        print("Tweet: " + tweets[tweet][0].encode('utf-8', 'replace').decode())
        print("------------------------------------------------------------")

def parse_trends(trends):
    #Loop through trends and print results
    for trend in trends:
        print("------------------------------------------------------------")
        print("Trending Topic: " + str(trends[trend]))
        print("Tweets per Trend: " + str(trend))
        print("------------------------------------------------------------")


if __name__ == '__main__':
    #Constants and AWS Key Configurations 
    TRENDS_WORD_CLOUD_URL = "https://1706224-tweets.s3.amazonaws.com/trends-wordcloud.png"
    TWEETS_WORD_CLOUD_URL = 'https://1706224-tweets.s3.amazonaws.com/tweets-wordcloud.png'
    TWEETS_WORDS_FREQ_URL = 'https://1706224-tweets.s3.amazonaws.com/word_frequencies.txt'
    LAMBDA_FUNCTION_NAME= "arn:aws:lambda:us-east-1:048071288123:function:getTweets"
    AWS_ACCESS_KEY_ID ="ASIAQWMKFUU5SOA7JKP6"
    AWS_SECRET_ACCESS_KEY ="CkFULUZEP3fQpC94Q1J/931mq2HdZ9YN6MFVmvv0"
    REGION = 'us-east-1'
    session = "IQoJb3JpZ2luX2VjEL3//////////wEaCXVzLXdlc3QtMiJHMEUCIQCHtEh0rGjYb2Bb8wbxsw71Qv3MXRAZvaW7Oy83UaTEswIgC5dgvY+oL6ikTiIrEKyLY8fi1iYqn9dkq2VIp3UswIgqtAIIRhAAGgwwNDgwNzEyODgxMjMiDM6EiqKN4rKVoWLmiyqRAmV67rZ0iJkteSRmP5Tqd7PpKoQ7WKYQURXwjrqj9SOziWKo+FMJXexUsSjVKIV2kQLo9CKPcZBQ6CrDza7unSn5VrNTj+vdVTDuWIfZB0mHN2+91+8RNN2XO7d+xZaPRQb8FS6oZJHegC62+nwMI4NoK6wTc/t4lkE9mplhB23oeId716m/KXQxspD5mB0QqMtqVV5yIWeOp6rjphBKOhwQS+dp33K2NlySq9tXJjjfnqeAKtZs918mpdq50Fv7bITCANfL6fEyhGMh+ISNhil+Zsb2+QDhgBYqtMgchA0V68hdTdVCi4IHcSQD1VNFLb0NCRSiTfhB2LeqsUg2Uc0L+qAif/b337rAEKWnTNzdajCr49SEBjqdASZU0bcf99T9Mmzz/wIzrKyVczBvIgC3W7jNU2LYnvd3DWduP9xDu6/9YHmDtsHU/r80vqieISH+WyNoQ9kt+5uuJYaAbhtzJ6DRM8xLbLXAKCeCuEcGGHfcBT6QIgg3l+i17aohpmHH/Y1d35dp0hJFN2yMdCNLCrNiw2EGwDQPC6RMyTRsNkLQRFY/XS2FiUtfXs8c5iz68nGQ5ok="
    #Create AWS client for lambda
    client = boto3.client('lambda',
                        region_name=REGION,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        aws_session_token = session)

    # Initilize Argument Parser
    parser = argparse.ArgumentParser(description="Twitter API Cloud Based Analytics")
    #Set Arguments
    parser.add_argument('function', help='Must collect either "tweets" or "trends"')
    parser.add_argument('amount', type=int, help='Amount of data to collect (Either 10, 30, 50)')
    parser.add_argument('time', type=int, help='How long to track data for Either 10, 30 or 60 mins (Only Applies to Tweets)')
    #Parse + Manage Arguments
    args = parser.parse_args()
    #Set payload for lambda context
    if args.function == "tweets":
        payload ={
                    "function": "tweets",
                     "amount": args.amount,
                     "time": args.time
        }
        #Call tweet lambda
        call_lambda_thread(payload, LAMBDA_FUNCTION_NAME)
        print("Tweets will update every 2 mins, please allow a full cycle for a complete list to generate")
        #Loop for set amount of mins, reading and printing updated tweets each time
        for _ in range (args.time):
            time.sleep(60)
            clearwindow()
            print("Tweets will update every min, please allow a full min for a complete list to generate")
            tweets = read_bucket("tweets.txt")
            parse_tweets(tweets)
            print("Word Cloud Generated at: "+TWEETS_WORD_CLOUD_URL)
            print("Tweet Analytics Generated at:" +TWEETS_WORDS_FREQ_URL)
            
    if args.function == "topics":
        payload ={
                    "function": "topics",
                     "amount": args.amount
        }
        #Call trend Lambda
        call_lambda_thread(payload, LAMBDA_FUNCTION_NAME)
        print("Fetching results please wait ... ")
        #Trend lambda does not run on time frame so wait for results and print 
        time.sleep(10) #Buffer to allow Function to run
        trends = read_bucket("trends.txt")
        parse_trends(trends)
        print("Word cloud Generated at: "+TRENDS_WORD_CLOUD_URL)
    else:
        print("Error Occured")
        raise Exception("ERROR: Please Ensure Arguments Are Passed Correctly, try -help for options")


