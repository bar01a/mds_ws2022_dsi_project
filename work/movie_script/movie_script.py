# Movie Script

# Short discription of what happens in this script: 

# Accessing and use the "Search Movies", "Get Reviews", "Get Popular" and "Get Details" endpoints of "The Movie Database API (https://developers.themoviedb.org/3/getting-started/introduction) to obtain the desired data:
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

# Install Kafka library:

# !pip install kafka-python

# Import necessary packages:

import requests
# from Hidden_Secret import myApiKey
import re
import json
from Kafka_Helpers import Producer, Consumer
import ast

# Note: Please don't delete this code cell yet!

# old version: get movie via title

# process data
# def get_data(movie_title):
    
    # "Avatar" as movie title example
    # receivedTitle = "Avatar"
    # received movie title from consumer (user)
    # receivedTitle = movie_title
    
    # apiKey = myApiKey["apiKey"]
    # apiKey = "105864a59e519ef281a74ca3af6c1b17"
    
    # request Search Movies endpoint
    # request1 = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=105864a59e519ef281a74ca3af6c1b17&query={receivedTitle}")
    # response1 = request1.json()
    # result1 = response1['results']
    # print(result1)
    
    # get id (from the first entry as this is the most similar to the received title)
    # movieID = [item['id'] for item in result1][0]    
    # print(movieID)
    
    # get original_title
    # movieTitle = [item['original_title'] for item in result1][0]
    # print(movieTitle)

    # request Get Reviews endpoint
    # request2 = requests.get(f"https://api.themoviedb.org/3/movie/{movieID}/reviews?api_key=105864a59e519ef281a74ca3af6c1b17")
    # response2 = request2.json()
    # result2 = response2['results']
    # print(result2)
    
    # get content
    # movieReviews = [item['content'] for item in result2]
    # movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews]
    # print(movieReviewsSplitted)
    
    # request Get Popular endpoint
    # request3 = requests.get("https://api.themoviedb.org/3/movie/popular?api_key=105864a59e519ef281a74ca3af6c1b17&")
    # response3 = request3.json()
    # result3 = response3['results']
    # print(result3)
    
    # get original_title from most popular movie (first entry since Get Popular updates daily)
    # mostPopularMovieTitle = [item['original_title'] for item in result3][0]
    # print(mostPopularMovieTitle)

    # there are currently no FSK 18 movies
    # get original_title from most popular movie adults
    # mostPopularMovieTitleAdult = [item['original_title'] for item in result3 if item['adult'] == True][0]
    # print(mostPopularMovieTitleAdults)
    
    # get original_title from most popular movie kids
    # mostPopularMovieTitleKids = [item['original_title'] for item in result3 if item['adult'] == False][0]
    # print(mostPopularMovieTitleKids)
    
    # return movieID, movieTitle, movieReviewsSplitted, mostPopularMovieTitle

# open Producer and write data into Kafka
# movieProducer = Producer('localhost', 29092)

# def handler(key, value):
#    movie_id, movie_title, movie_reviews, most_pop_movie = get_data(value)
#    movieProducer.send("movie_reviews", "key", json.dumps({
#        "id": movie_id, 
#        "movie_title": movie_title, 
#        "reviews": movie_reviews, 
#        "pop": most_pop_movie
#    }))

# open Consumer read data from Kafka
# movieConsumer = Consumer('localhost', 29092, "new_movie_title", handler)

# Process data:

# new version:
# get_data_by_title: get movieID, movieTitle and movieReviewsSplitted via movie_title
# get_data_of_most_popular_movie: get movieID, movieTitle and movieReviewsSplitted via get_most_pop

# process data by the function get_data_by_title(movie_title)
def get_data_by_title(title):
    # "Avatar" as movie title example
    receivedTitle = "Avatar"
    # received movie title from consumer (user)
    # receivedTitle = title
    
    # apiKey = myApiKey["apiKey"]
    apiKey = "105864a59e519ef281a74ca3af6c1b17"
    
    # request Search Movies endpoint
    request1 = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=105864a59e519ef281a74ca3af6c1b17&query={receivedTitle}")
    response1 = request1.json()
    result1 = response1['results']
    # print(result1)

    # get id (from the first entry as this is the most similar to the received title)
    movieID = [item['id'] for item in result1][0]    
    # print(movieID)
    
    # get original_title (from the frist entry, machting the id)
    movieTitle = [item['original_title'] for item in result1][0]
    # print(movieTitle)
    
    # request Get Reviews endpoint
    request2 = requests.get(f"https://api.themoviedb.org/3/movie/{movieID}/reviews?api_key=105864a59e519ef281a74ca3af6c1b17")
    response2 = request2.json()
    result2 = response2['results']
    # print(result2)
    
    # get content (matching the id)
    movieReviews = [item['content'] for item in result2]
    movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews]
    # print(movieReviewsSplitted)
    
    return movieID, movieTitle, movieReviewsSplitted

# process data by the function get_data_of_most_popular_movie()
def get_data_of_most_popular_movie(): 
    
    # get id of most popular movie which has the most reviews 
    # (since reviews are essential for the creation of the wordcloud but there are most popular movies without any reviews)
    movieID = 0
    maxReviews = 0
    
    # request Get Popular endpoint
    request1 = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=105864a59e519ef281a74ca3af6c1b17&')
    response1 = json.loads(request1.text)

    for movie in response1['results']:
        movie_ID = movie['id']
        # request Get Reviews endpoint
        request1 = requests.get(f'https://api.themoviedb.org/3/movie/{movie_ID}/reviews?api_key=105864a59e519ef281a74ca3af6c1b17')
        response1 = json.loads(request1.text)
        # get id of most popular movie with most reviews
        if len(response1['results']) > max_reviews:
            maxReviews = len(response1['results'])
            movieID = movie_id
        
    # print(movieID)
    
    # request Get Details endpoint (with the id that was just defined)
    request2 = requests.get(f"https://api.themoviedb.org/3/movie/{movieID}?api_key=105864a59e519ef281a74ca3af6c1b17&language=en-US")
    response2 = request2.json()
    
    # get original_title (matching the id)
    movieTitle = [response2['original_title']]
    # print(movieTitle)
    
    # request Get Reviews endpoint
    result = response1['results']
    
    # get content (matching the id)
    movieReviews = [item['content'] for item in result]
    movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews]
    # print(movieReviews)

    return movieID, movieTitle, movieReviewsSplitted

# Write processed data into Kafka:

# open Producer and write data into Kafka
movieProducer = Producer('kafka', 9092)

def handler(key, value):
    # check what is inside the message from the consumer
    if "movie-title=" in str(value):
        title = value.replace("movie-title=","")
        movide_id, movie_title, movie_reviews = get_data_by_title(title)
    if "get_most_pop" in str(value):
        movie_id, movie_title, movie_reviews = get_data_of_most_popular_movie()
    # write data into Kafka
    movieProducer.send("movie_reviews", "key", json.dumps({
        "id": movie_id, 
        "movie_title": movie_title, 
        "reviews": movie_reviews
    }))
    
# Open consumer and read data from Kafka:

# open Consumer read data from Kafka
movieConsumer = Consumer('kafka', 9092, "new_movie_title", handler)