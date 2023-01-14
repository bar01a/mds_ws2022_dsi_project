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
    o = json.loads(value)
    o['movie_id'] = str(o['movie_id']).replace("'", '').replace('[', '').replace(']', '')
    o['title'] = str(o['title']).replace("'", '').replace('[', '').replace(']', '')
    o['reviews'] = ast.literal_eval(str(o['reviews']))
    
    if not check_if_movie_exists_in_mongodb(movie_id):
        client = MongoClient('mongodb_container', 27017,
                        username='root',
                        password='rootpassword')
        db = client['movies']
        collection = db['reviews']
        # text = text.replace("'", '"')
        collection.insert_one(o)

def check_if_movie_exists_in_mongodb(movie_id):
    try:
        client = MongoClient('mongodb_container', 27017,
                     username='root',
                     password='rootpassword')
        db = client['movies']
        collection = db['reviews']
        res = collection.find_one({'movie_id': str(movie_id)})
        if res is not None:
            return True
        else:
            return False
    except:
        return False

def load_movie_from_mongodb_if_exists(movie_id, default=(None, None)):
    client = MongoClient('mongodb_container', 27017,
                         username='root',
                         password='rootpassword')
    db = client['movies']
    collection = db['reviews']
    res = collection.find_one({'movie_id': movie_id})
    if res is not None:
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
    # text, counted_words = load_text_from_file()
    if text is not None:
        wordcloud = WordCloud(max_words=20).generate(text)

        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(wordcloud, interpolation='bilinear')
        header.title(movie_title)
        subheader.subheader("Wordcloud for movie id: " + str(movie_id))
        cloud.pyplot(fig)
        subheader2.subheader("Top 30 most frequent words (without any filter):")
        # sort counted_words by value
        df = pd.DataFrame(counted_words, columns=['word', 'count'])
        df = df.sort_values(by=['count'], ascending=False)
        list_count.table(df.head(30))
        # df without row index
        list_count.dataframe(df.head(30), width=1000, height=1000)
    else:
        st.info(f"No reviews found for {movie_title} with id {movie_id}")

def check_timeout(timeout, handler):
    time.sleep(timeout)
    handler(True)

def set_timeout(new_state):
    global timeout_occurred
    timeout_occurred = new_state

def prepare_sidebar():
    st.sidebar.title("Movie Wordcloud Generator")
    input_no = st.sidebar.text_input("Enter any movie-id :point_down:")
    button_state = st.sidebar.button("Show me the wordcloud!")
    st.sidebar.write("(33, 77, 76600)")
    st.sidebar.markdown("---")
    button_most_pop = st.sidebar.button("Show most popular movie")
    button_most_pop_kids = st.sidebar.button("Show most popular kids movie")
    st.sidebar.markdown("---")
    button_clear_db = st.sidebar.button("Clear Cache-MongoDB")
    return input_no, button_state, button_clear_db, button_most_pop, button_most_pop_kids

Consumer(server='kafka', port=9092, topic_name='adjectives_counted', handler=handle_message)
my_producer = Producer(server='kafka', port=9092)

input_no, button_state, button_clear_db, button_most_pop, button_most_pop_kids = prepare_sidebar()

if button_state or input_no:
    # check if input_no is a number
    if input_no.isnumeric():
        loading = True
        text, counted_words = (None, None)

        if check_if_movie_exists_in_mongodb(input_no) == False:
            with st.spinner('Data not in Cache-MongoDB, loading from API :wink:...'):
                key_bytes = bytes('data', encoding='utf-8')
                my_producer.send(topic_name='new_movie_id', key=key_bytes, value=input_no)
                x = threading.Thread(target=check_timeout, args=(10, set_timeout))
                x.start()
                while loading and not timeout_occurred:
                    time.sleep(0.1)

        if timeout_occurred:
            st.error("Timeout occurred. Please try again later.")
        else:
            time.sleep(1)
            text, counted_words = load_movie_from_mongodb_if_exists(input_no)
            if text is None:
                st.error("No reviews found for movie-id: " + input_no)
            else:
                get_wordcloud(text, counted_words)
    else:
        st.sidebar.error("Please enter a movie-id :point_up:")

if button_most_pop:
    st.sidebar.warning("Not implemented yet :sweat_smile:")

if button_most_pop_kids:
    st.sidebar.warning("Not implemented yet :sweat_smile:")

if button_clear_db:
    client = MongoClient('mongodb_container', 27017, username='root', password='rootpassword')
    db = client['movies']
    collection = db['reviews']
    collection.delete_many({})
    st.sidebar.success("Cache cleared! :sunglasses:")
