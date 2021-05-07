from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import boto3



def generate_word_cloud(text, FILE_NAME):
    wordcloud = WordCloud(width = 3000, 
                        height = 2000, 
                        random_state=1, 
                        background_color='salmon', 
                        colormap='Pastel1', 
                        collocations=False, 
                        stopwords = STOPWORDS).generate(text)
    wordcloud.to_file("/tmp/"+FILE_NAME)
    save_to_bucket(wordcloud, FILE_NAME)


def save_to_bucket(wordcloud, FILE_NAME):
    #Save tweet list to an s3 bucket
    BUCKET_NAME = "1706224-tweets"
    s3 = boto3.client('s3')
    s3.upload_file("/tmp/"+FILE_NAME,BUCKET_NAME,FILE_NAME)
  
