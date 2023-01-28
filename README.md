# TLDR; Filmrezensionen | 20-Wort-Konsensus

*Dokumentation zum Abschlussprojekt zur LV "Data Science Infrastructure"*

### Team

-   Yvonne Gisser
-   Dusan Resavac
-   Roland Bauer

### Ziel / Ergebnis

Das Ziel / Ergebnis dieses Projekts besteht darin, Filmrezensionen auf eine einfache sowie anschauliche Art zusammenzufassen, sodass der Konsens verschiedener Meinungen auf einem einzigen Blick ersichtbar ist. Dies wird anhand einer Webapplikation zum Anzeigen einer Wordcloud realisiert, welche die, aus Filmrezensionen am häufigst vorkommenden, Adjektive darstellt (wobei max. die 20 am häufigst vorkommenden Adjektive verwendet werden, um eine einfache Lesbarkeit der Wordcloud sicherzustellen).

### Architektur

Die Architektur dieses Projekts ist folgendermaßen aufgebaut:

![Architektur](architecture.png)

Dementsprechend gibt es **4 Microservices** mit **Kafka** als zentralen Message Broker. 

Um ein besseres Verständnis für diese Microservices zu schaffen, werden sie in den kommenden Absätzen genauer beschrieben: 

**1. Streamlit Script (siehe in der Architektur rechts unten):**

Das Streamlit Script (in der Verzeichnisstruktur unter worldcloud_app zu finden) stellt das Frontend des Projekts dar. Dabei kann der/die Endbenutzer*in 3 verschiedene Aktionen ausführen:
   - Er/Sie kann einen beliebigen Filmtitel eingeben und sich somit die Wordcloud der dazugehörigen Filmrezensionen anzeigen lassen,  
   - sich die Wordcloud der Filmrezensionen des aktuell populärsten Films anzeigen lassen (dieser wird täglich aktualisiert) und
   - die Caching-Datenbank leeren.
       
**2. Filme Script (siehe in der Architektur rechts oben):**

Das Filme Script (in der Verzeichnisstruktur unter movie_script zu finden) empfängt die Anfragen für neue Filmrezensionen via Kafka vom Streamlit Script, holt sich die notwendigen Daten (= movie title, movie ID und movie reviews) aus der Movie DB und sendet diese zurück an Kafka.
   
**3. Wörterbuch Script (siehe in der Architektur links oben):**

Das Wörterbuch Script (in der Verzeichnisstruktur unter dictionary_script zu finden) lädt beim Starten des Containers, je nach übergebenem Argument (über docker-compose.yml konfigurierbar), die Adjektive aus der entsprechenden Quelle, empfängt die Anfragen via Kafka vom Filme Script, filtert die Filmrezensionen nach deren Adjektiven und sendet schließlich die gefilterten Rezensionen gemeinsam mit der movie ID und dem movie titel zurück an Kafka.

**4. Spark Script (siehe in der Architektur links unten):**

Das Spark Script (in der Verzeichnisstruktur unter Spark_script zu finden) wird für einerseits für Analysezwecke verwendet, dh. es
   - vereint die json-Dateien, die eine mögliche Quelle für Adjektive darstellen und transformiert den Inhalt in eine einzelne json-Datei, 
   - ermittelt die Anzahl aller adjektivischer Bedeutungen jedes Wortes und
   - gibt die Anzahl an Wörtern zurück, die zumindest eine adjektivische Bedeutung haben.

Andererseits empfängt es aber auch neue Anfragen (gefiltert) via Kafka vom Wörterbuch Script, macht ein Wordcount der Adjektive und sendet die empfangenen Daten und die Wordcounts wieder an Kafka. 

Um ebenfalls ein besseres Verständnis für Kafka als zentralen Message Broker zu schaffen, werden im kommen Absatz die einzelnen Kafka Topics beschrieben: 

**1. "new_movie_title"**: 

Streamlit Script --> Filme Script

**2. "movie_reviews"**: 

Filme Script --> Wörterbuch Script 

**3. "adjectives"**: 

Wörterbuch Script --> Spark Script 

**4. "adjectives_counted"**: 

Spark Script --> Streamlit Script

### Setup

1. `docker-compose up -d` ausführen
2. Jupyter öffnen und `!pip install kafka-python` ausführen
3. Code chunk **wordcount** in JupyterLab innerhalb des Jupyter/Spark-Containers starten
4. <a href="http://localhost:8501/" target="_blank">Wordcloud App</a> öffnen

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
