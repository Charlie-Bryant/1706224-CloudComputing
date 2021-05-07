import boto3
import json
from getWordCloud import generate_word_cloud

def getTopics(amount, api):
    #init empty dictionary and counter
        trends = {}
        total_trends = 0
        #Collect trend based on UK area code
        data = api.trends_place(23424975)
        for trend in data[0]['trends']: 
                #Loop through trends and collected desired amount
                trends[trend['tweet_volume']] = trend['name']
                print(trend['tweet_volume'])
                #Calculate total trends
                total_trends += int(trend['tweet_volume'] or 0)
                #Break if total is over desired amount
                if len(trends) >= amount:
                    break
        #Generate Analytics
        trends["total interactions"] = total_trends
        trends["average interactions"] = total_trends/len(trends)
        save_to_bucket(trends)
        generate_metrics(trends)
    
        return trends
  
def save_to_bucket(trends):
    #Save trends to s3 
    BUCKET_NAME = "1706224-tweets"
    FILE_NAME = "trends.txt"
    s3 = boto3.resource('s3')
    object = s3.Object(BUCKET_NAME, FILE_NAME)
    object.put(Body=(bytes(json.dumps(trends, indent=2).encode('UTF-8'))))
    
    
def generate_metrics(trends):
    #Add all trends to string based on how many times they are tweeted about
    trendlist=""
    for trend in trends:
        #Check if trend is an int and not None Type
        if isinstance(trend, int):
            for _ in range(trend):
                trendlist+=str(trends[trend])+" "
        else:
            trendlist+=str(trends[trend])+" "
    #Generate word cloud based on trends
    generate_word_cloud(trendlist, 'trends-wordcloud.png')
        
    