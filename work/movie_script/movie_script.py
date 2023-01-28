# Movie Script

# Short discription of what happens in this script: 

# Accessing and use the "Search Movies", "Get Reviews", "Get Popular" and "Get Details" endpoints of "The Movie Database (TMDB)"-API (https://developers.themoviedb.org/3/getting-started/introduction) to obtain the desired data:
# * In case the user specifies a movie title: 
#     - the movie title that was requested
#     - the corresponding movie ID 
#     - the corresponding movie reviews

# * In case the user requests the most popular movie:
#     - the most popular movie title which has the most reviews
#     - the corresponding movie ID 
#     - the corresponding movie reviews

# Writing this data into Kafka via the Kafka "movieProducer" & reading the requested movie title or the requested most popular movie via the Kafka "movieConsumer".

# The individual steps:

# Import necessary packages:
import requests
import re
import json
from Kafka_Helpers import Producer, Consumer
import ast
from Hidden_Secret import moviedb_api_key

# KAFKA CONFIG:
KAFKA_SERVER = 'kafka'
KAFKA_PORT = 9092
KAFKA_TOPIC_CONSUME = 'new_movie_title'
KAFKA_TOPIC_PRODUCE = 'movie_reviews'

# process data by the function get_data_by_title(title):
def get_data_by_title(title):
    # received movie title from consumer (user)
    receivedTitle = title
    
    apiKey = moviedb_api_key
    
    # request Search Movies endpoint
    request1 = requests.get(f"https://api.themoviedb.org/3/search/movie", {"api_key": apiKey, "query": receivedTitle})
    response1 = request1.json()
    result1 = response1['results']

    # get id (from the first entry as this is the most similar to the received title)
    movieID = [item['id'] for item in result1][0]    
    
    # get original_title (from the frist entry, machting the id)
    movieTitle = [item['original_title'] for item in result1][0]
    
    # request Get Reviews endpoint
    request2 = requests.get(f"https://api.themoviedb.org/3/movie/{movieID}/reviews", {"api_key": apiKey})
    response2 = request2.json()
    result2 = response2['results']
    
    # get content (matching the id)
    movieReviews = [item['content'] for item in result2]
    movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews]
    
    return movieID, movieTitle, movieReviewsSplitted

# process data by the function get_data_of_most_popular_movie():
def get_data_of_most_popular_movie():

    apiKey = moviedb_api_key
    
    # get id of most popular movie which has the most reviews 
    # (since reviews are essential for the creation of the wordcloud but there are most popular movies without any reviews)
    movieID = 0
    maxReviews = 0
    reviews_of_most_popular_movie = []
    
    # request Get Popular endpoint
    request1 = requests.get(f"https://api.themoviedb.org/3/movie/popular", {"api_key": apiKey})
    response1 = json.loads(request1.text)

    for movie in response1['results']:
        movie_ID = movie['id']
        # request Get Reviews endpoint
        request1 = requests.get(f"https://api.themoviedb.org/3/movie/{movie_ID}/reviews", {"api_key": apiKey})
        response1 = json.loads(request1.text)
        # get id of most popular movie with most reviews
        if len(response1['results']) > maxReviews:
            maxReviews = len(response1['results'])
            movieID = movie_ID
            reviews_of_most_popular_movie = response1['results']
        
    # request Get Details endpoint (with the id that was just defined)
    request2 = requests.get(f"https://api.themoviedb.org/3/movie/{movieID}", {"api_key": apiKey, "language": "en-US"})
    response2 = request2.json()
    
    # get original_title (matching the id)
    movieTitle = [response2['original_title']]
    
    # request Get Reviews endpoint
    result = reviews_of_most_popular_movie
    
    # get content (matching the id)
    movieReviews = [item['content'] for item in result]
    movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews]

    return movieID, movieTitle, movieReviewsSplitted

# Write processed data into Kafka:
# open Producer and write data into Kafka
movieProducer = Producer(KAFKA_SERVER, KAFKA_PORT)

def handler(key, value):
    # check what is inside the message from the consumer
    if "movie-title=" in str(value):
        title = value.replace("movie-title=","")
        movie_id, movie_title, movie_reviews = get_data_by_title(title)
    if "get_most_pop" in str(value):
        movie_id, movie_title, movie_reviews = get_data_of_most_popular_movie()
    # write data into Kafka
    movieProducer.send(KAFKA_TOPIC_PRODUCE, "key", json.dumps({
        "movie_id": movie_id, 
        "title": movie_title, 
        "reviews": movie_reviews
    }))

# Read data from Kafka:    
# open Consumer read data from Kafka
movieConsumer = Consumer(KAFKA_SERVER, KAFKA_PORT, KAFKA_TOPIC_CONSUME, handler)