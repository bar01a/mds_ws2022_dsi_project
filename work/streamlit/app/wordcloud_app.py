import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from Kafka_Helpers import Consumer, Producer
import ast
import pandas as pd
from pymongo import MongoClient
import time
import json
import threading

header = st.empty()
subheader = st.empty()
cloud = st.empty()
subheader2 = st.empty()
list_count = st.empty()
loading = False
movie_id = 0
movie_title = ""
timeout_occurred = False

# KAFKA CONFIG
KAFKA_SERVER = 'localhost'
KAFKA_PORT = 29092
NEW_KAFKA_REQUEST_TOPIC = 'topic_A'

# MONGODB CONFIG
MONGO_SERVER = 'mongodb_container'
MONGO_SERVER = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = 'root'
MONGO_PASSWORD = 'rootpassword'

def get_mongo_client():
    return MongoClient(MONGO_SERVER, MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD)

def prepare_data(data, default=(None, None)):
    global movie_id, movie_title
    if data is not None:
        movie_id = data['movie_id']
        movie_title = data['title']
        l = ast.literal_eval(str(data['reviews']))
        temp = [item for sublist in l for item in sublist]
        if len(movie_title) != 0 and len(temp) == 0:
            return default
        word_list = ", ".join(temp)
        counted_words = data['counted_words']
        return word_list, counted_words
    else:
        return default

def write_movie_to_mongodb(value):
    global movie_id, movie_title, counter
    o = json.loads(value)
    o['movie_id'] = str(o['movie_id']).replace("'", '').replace('[', '').replace(']', '')
    o['title'] = str(o['title']).replace("'", '').replace('[', '').replace(']', '')
    movie_title = o['title']
    
    if check_if_movie_exists_in_mongodb_by_title(o['title']) is False:
        o['reviews'] = ast.literal_eval(str(o['reviews']))
        client = get_mongo_client()
        db = client['movies']
        collection = db['reviews']
        collection.insert_one(o)
        client.close()

def check_if_movie_exists_in_mongodb(movie_id):
    try:
        client = get_mongo_client()
        db = client['movies']
        collection = db['reviews']
        res = collection.find_one({'movie_id': str(movie_id)})
        return (res is not None)
    except:
        return False

def check_if_movie_exists_in_mongodb_by_title(title):
    try:
        client = get_mongo_client()
        db = client['movies']
        collection = db['reviews']
        res = collection.find_one({'title': title})
        return (res is not None)
    except:
        return False

def load_movie_from_mongodb_if_exists(movie_id, default=(None, None)):
    client = get_mongo_client()
    db = client['movies']
    collection = db['reviews']
    res = collection.find_one({'movie_id': movie_id})
    if res is not None:
        return prepare_data(res, default)
    else:
        return default

def load_movie_from_mongodb_by_title(title, default=(None, None)):
    global movie_id, movie_title
    client = get_mongo_client()
    db = client['movies']
    collection = db['reviews']
    res = collection.find_one({'title': title})
    if res is not None:
        movie_id = res['movie_id']
        movie_title = res['title']
        return prepare_data(res, default)
    else:
        return default

def handle_message(key, value):
    global loading
    loading = False
    write_movie_to_mongodb(value)
    time.sleep(0.5)
    loading = False

def get_wordcloud(text, counted_words):
    global movie_id, movie_title
    header.title(movie_title)
    subheader.subheader("Wordcloud for movie id: " + str(movie_id))
    if text is not None:
        wordcloud = WordCloud(max_words=20).generate(text)

        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(wordcloud, interpolation='bilinear')
        cloud.pyplot(fig)
        subheader2.subheader("Top 30 most frequent words (without any filter):")
        # sort counted_words by value
        df = pd.DataFrame(counted_words, columns=['word', 'count'])
        df = df.sort_values(by=['count'], ascending=False)
        list_count.table(df.head(30))
        # df without row index
        list_count.dataframe(df.head(30), width=1000, height=1000)
    else:
        st.info(f'No reviews found for "{movie_title}" with id {movie_id}')

def check_timeout(timeout, handler):
    time.sleep(timeout)
    handler(True)

def set_timeout(new_state):
    global timeout_occurred
    timeout_occurred = new_state

def prepare_sidebar():
    st.sidebar.title("Movie Wordcloud Generator")
    input_no = st.sidebar.text_input("Enter any movie-title :point_down:")
    button_state = st.sidebar.button("Show me the wordcloud!")
    # st.sidebar.write("(33, 77, 76600)")
    st.sidebar.markdown("---")
    button_most_pop = st.sidebar.button("Show most popular movie")
    # button_most_pop_kids = st.sidebar.button("Show most popular kids movie")
    st.sidebar.markdown("---")
    button_clear_db = st.sidebar.button("Clear Cache-MongoDB")
    return input_no, button_state, button_clear_db, button_most_pop

Consumer(server=KAFKA_SERVER, port=KAFKA_PORT, topic_name='topic_D', handler=handle_message)
my_producer = Producer(server=KAFKA_SERVER, port=KAFKA_PORT)

input_no, button_state, button_clear_db, button_most_pop = prepare_sidebar()

if button_state:
    # check if input_no has at least lenght 1
    if len(input_no) > 0:
        loading = True
        text, counted_words = (None, None)

        if check_if_movie_exists_in_mongodb_by_title(input_no) == False:
            with st.spinner('Data not in Cache-MongoDB, loading from API :wink:...'):
                key_bytes = bytes(NEW_KAFKA_REQUEST_TOPIC, encoding='utf-8')
                my_producer.send(topic_name=NEW_KAFKA_REQUEST_TOPIC, key=key_bytes, value=f'movie-title={input_no}')
                x = threading.Thread(target=check_timeout, args=(15, set_timeout))
                x.start()
                while loading and not timeout_occurred:
                    time.sleep(0.1)

        if timeout_occurred:
            st.error("Timeout occurred. Please try again later.")
        else:
            loading = False
            time.sleep(1)
            text, counted_words = load_movie_from_mongodb_by_title(input_no)
            get_wordcloud(text, counted_words)
    else:
        st.sidebar.error("Please enter a title :point_up:")

if button_most_pop:
    loading = True
    text, counted_words = (None, None)

    with st.spinner('Loading most popular movie from API :wink:...'):
        key_bytes = bytes(NEW_KAFKA_REQUEST_TOPIC, encoding='utf-8')
        my_producer.send(topic_name=NEW_KAFKA_REQUEST_TOPIC, key=key_bytes, value="get_most_pop")
        x = threading.Thread(target=check_timeout, args=(10, set_timeout))
        x.start()
        while loading and not timeout_occurred:
            time.sleep(0.1)

    if timeout_occurred:
        st.error("Timeout occurred. Please try again later.")
    else:
        time.sleep(1)
        text, counted_words = load_movie_from_mongodb_by_title(movie_title)
        get_wordcloud(text, counted_words)

if button_clear_db:
    client = get_mongo_client()
    db = client['movies']
    collection = db['reviews']
    collection.delete_many({})
    st.sidebar.success("Cache cleared! :sunglasses:")
