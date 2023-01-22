# mds_ws2022_dsi_project

Data Science Infrastructure project

### Meeting 2022-01-08

alles (außer Spark-Script) in docker!

SparkSQL? Wo sollen wir es einbauen?

kafka topics

1. new_movie_id (Streamlit --> Movie-Script)
2. movie_reviews (Movie-Script --> Dict.-Script)
3. adjectives (Dict.-Script --> Spark-Script)
4. adjectives_counted (Spark-Script --> Streamlit)

API Wrapper Libs:

-   könnten für Movie-Script hilfreich sein
-   https://www.themoviedb.org/documentation/api/wrappers-libraries

Möglichkeiten um Filme abzufragen:

1. Titel

-   movie-title=avatar
-   movie-title=unforgiven

2. Get most popular movie

-   get_most_pop

2. Get most popular kids movie

-   get_most_pop_kids

### Possible search phrases

#### short search phrases with reviews

-   Matrix
-   Captain
-   matrix
-   matrix revolutions
-   captain

#### short search without reviews

-   green
-   forest

#### full movie titles

-   The Matrix
-   Captain Marvel
-   The Matrix Revolutions
