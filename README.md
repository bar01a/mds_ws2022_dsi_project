# mds_ws2022_dsi_project

Data Science Infrastructure project

### Ziel



### Architektur

Insgesamt 4 **Microservices** mit **Kafka** als zentralen Message Broker:

1. Wordcloud App
    - Frontend
2. Movie Script
    - empfängt Requests für neue Reviews via Kafka von Wordcloud
    - holt Daten von der Movie API
    - sendet Daten (Movie ID, Titel und Reviews) wieder an Kafka
3. Dictionary Script
    - empfängt neue Reviews von Movie Script
    - filtert Reviews nach Adjektiven
    - sendet gefilterte Reviews gemeinsam mit Movie ID und Titel wieder an Kafka
4. Spark Script
    - Analysezwecke
      - vereint die json-Dateien, die eine mögliche Quelle für Adjektive darstellen, und transformiert den Inhalt in eine einzelne json-Datei
      - zählt die Anzahl aller adjektivischen Bedeutungen jedes Worts
      - gibt die Anzahl an Wörter zurück, die zumindest eine adjektivische Bedeutung haben
    - empfängt neue Reviews (gefiltert) von Dictionary Script
    - macht Wordcount der Adjektive
    - sendet empfangene Daten + Wordcounts wieder an Kafka

### Kafka topics

1. **new_movie_title** (Wordcloud App --> Movie Script)
2. **movie_reviews** (Movie Script --> Dictionary Script)
3. **adjectives** (Dictionary Script --> Spark Script)
4. **adjectives_counted** (Spark Script --> Wordcloud App)

### Setup

1. ```docker-compose up -d``` ausführen
2. Jupyter öffnen und ```!pip install kafka-python``` ausführen
3. Wordcloud App öffnen (```localhost:8501```)

### Features

1. Film über Titel abfragen (Freitextfeld)
2. Most popular Film abfragen
3. Cache-Tabelle löschen

### Possible search phrases

#### short search phrases with reviews

-   Matrix
-   Captain
-   matrix
-   matrix revolutions
-   captain
-   unforgiven

#### short search without reviews

-   green
-   forest

#### full movie titles

-   The Matrix
-   Captain Marvel
-   The Matrix Revolutions
-   Unforgiven