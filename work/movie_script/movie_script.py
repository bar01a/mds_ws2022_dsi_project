import requests
# from Hidden_Secret import myApiKey
import re
import json
from Kafka_Helpers import Producer, Consumer

# Note: Please don't delete this code cell yet!

# old version: get movie via ID

def get_data(movie_id):
    exampleID = movie_id
    #apiKey = myApiKey["apiKey"]
    apiKey = "105864a59e519ef281a74ca3af6c1b17"

    request1 = requests.get(f"https://api.themoviedb.org/3/movie/{exampleID}?api_key=105864a59e519ef281a74ca3af6c1b17&language=en-US")
    response1 = request1.json()

    request2 = requests.get(f"https://api.themoviedb.org/3/movie/{exampleID}/reviews?&language=en-US&page=1", {"api_key": apiKey})
    response2 = request2.json()
    result = response2['results']

    # ID
    movieID = [response1['id']]

    # original_title
    movieTitle = [response1['original_title']]

    # content
    movieReviews = [item['content'] for item in result]
    movieReviewsSplitted = [re.sub(r"[^\w \- \  ]", "", item.lower()).split(" ") for item in movieReviews] # ToDo: How to ignore empty string?
    return movieID, movieTitle, movieReviewsSplitted

movieProducer = Producer('kafka', 9092)

def my_test_handler(key, value):
   movie_id, movie_title, movie_reviews = get_data(value)
   movieProducer.send("movie_reviews", "key", json.dumps({
       "movie_id": movie_id,
       "title": movie_title,
       "reviews": movie_reviews
   }))

movieConsumer = Consumer('kafka', 9092, "new_movie_id", my_test_handler)
