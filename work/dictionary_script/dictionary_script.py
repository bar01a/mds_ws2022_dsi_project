import re
import os
import redis
import json
import sys, getopt
from Kafka_Helpers import Producer, Consumer

# Natural Language Toolkit already offers many libraries regarding computer linguistics
# E.g. "from nltk.corpus import wordnet as wn" could be used to categorise the part of speech of a given word
# For education's sake, we try to create our own list of adjectives using Wordnet and/or a json file

# allowed_specials (syntactic markers)
# p predicate position
# a prenominal (attributive) position
# ip immediately postnominal position
def read_word_net_dictionary(file_path, allowed_specials = [], allow_adjective_satellite = True):
    adjectives_word_net = set()

    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        #https://wordnet.princeton.edu/documentation/wndb5wn
        #https://wordnet.princeton.edu/documentation/wninput5wn
        # word with opt. info (.) followed by space + hexCode + space
        match = re.search(r"\d+ \w{2} (\w) \w{2} ((?:[a-zA-Z_\-.']+(?:\((a|p|ip)\))? [0-9a-fA-F] )+)", line)
        if match is not None:
            # between words is a one-digit hex code distinctly identifying a word within a lexicographer's file
            words = re.sub(r" [0-9a-fA-F] ", " ", match.group(2)).strip()
            # replace multiple spaces with single space
            words = re.sub(r" +", " ", words).split(" ")
            for word in words:
                # _ in word means space -> two words | remove all words which are adjectives only in a certain context | potentially remove adjective satellite
                syntactic_marker_match = re.search(r'\((.{1,2})\)$', word)
                # if no markers exist or this marker is whitelisted
                is_marker_allowed = syntactic_marker_match is None or syntactic_marker_match.group(1) in allowed_specials
                # if adjective satellites are allowed, or it isn't an adjective satellite
                show_adjective_satellites = allow_adjective_satellite or match.group(1) != 's'
                if "_" not in word and show_adjective_satellites and is_marker_allowed:
                    word = re.sub(r"\(.+\)", "", word)
                    adjectives_word_net.add(word.lower())
    return adjectives_word_net


def read_nltk_extraction(directory_path):
    adjectives_nltk = set()

    # traverse directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # if path leads to file
        if os.path.isfile(file_path):
            # open file and read as json
            with open(file_path, "r") as file:
                file_json = json.load(file)
            # loop through json dictionary entries
            for key, value in file_json.items():
                # if meanings is empty
                if value['MEANINGS'] is None or not value['MEANINGS']:
                    continue
                for key_meaning, value_meaning in value['MEANINGS'].items():
                    # only take first meaning into consideration - if not enough adjectives are found, evaluate better approach
                    # e.g. by taking words whose adjective-meanings make up >= 50% of all meanings
                    if value_meaning[0].lower() == 'adjective':
                        adjectives_nltk.add(key.lower())
                    break
    return adjectives_nltk


def flush_and_fill_redis(redis_connection, adjectives_dict):
    # remove existing entries
    redis_connection.flushdb()
    pipe = redis_connection.pipeline() # create a pipeline instance
    for adjective in adjectives_dict:
        # insert adjective into redis db
        # the value is irrelevant if single keys are accessed but has to be the word if redis pipelines are used during retrieval
        pipe.set(adjective, adjective)
    pipe.execute()  # the EXECUTE call sends all buffered commands to the server

    print(f'Number of adjectives: {len(adjectives_dict)}')

    # test - value is string if not None (weird, but okay)
    assert redis_connection.get('excited') == 'excited'
    assert redis_connection.get('house') is None


adjectives = set()


# switch case
def get_dataset(dataset):
    return {
        # using dictionary json
        'nltk': read_nltk_extraction('./data/Dictionary JSON'),
        # without adjective satellites
        'wordnet': read_word_net_dictionary("./data/adjectives_wordnet.adj", [], False),
        # all adjectives + markers
        'wordnet_all': read_word_net_dictionary("./data/adjectives_wordnet.adj", ['a', 'ip', 'p'], True),
    }.get(dataset, read_nltk_extraction('./data/Dictionary JSON'))


clear_redis = False

print(f"Arguments: {str(sys.argv)}")

opts, args = getopt.getopt(sys.argv[1:], "d:c", ["dataset=","clear"])
for opt, arg in opts:
    if opt in ['-d', '--dataset']:
        adjectives = get_dataset(arg)
        clear_redis = True
        print(f"Argument --dataset {arg} found. Got {len(adjectives)} adjectives and will refresh database.")
    elif opt in ("-c", "--clear"):
        clear_redis = True
        print("Argument --clear found. Fill refresh database.")

if len(adjectives) == 0:
    adjectives = read_nltk_extraction('./data/Dictionary JSON')

# preview
print(list(adjectives)[0:10])

# create connection to redis db
redis_conn = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

if clear_redis:
    # clear and fill redis
    flush_and_fill_redis(redis_conn, adjectives)

# fill blacklist if necessary
blacklist = { }

dictionary_producer = Producer('kafka', 9092)

def subscribe_handler(key, value):
    print('got')
    infos_and_reviews = json.loads(value)
    reviews = infos_and_reviews['reviews']

    pipe = redis_conn.pipeline()  # create a pipeline instance

    # ignore result which is going to be a list of some sort of pipeline objects
    [pipe.get(word) for review in reviews for word in review]  # for each word call get on pipe

    # send pipe buffer at once and receive all adjectives in reviews
    adjectives_in_reviews = set(pipe.execute())
    adjectives_in_reviews.remove(None)

    # unfortunately, loop through reviews again otherwise the knowledge of which word belongs to which review is lost
    # If that is unimportant, adjectives_in_reviews should be a list (not a set)
    reviews_words = [[word for word in review if word not in blacklist and word in adjectives_in_reviews] for review in reviews]

    dictionary_producer.send('adjectives', key, {
        'movie_id': infos_and_reviews['movie_id'],
        'title': infos_and_reviews['title'],
        'reviews': reviews_words
    })

    print('sent')


dictionary_consumer = Consumer('kafka', 9092, 'movie_reviews', subscribe_handler)
