# TLDR; Filmrezensionen | 20-Wort-Konsensus

*Dokumentation zum Abschlussprojekt zur LV "Data Science Infrastructure"*

## Team

-   Yvonne Gisser
-   Dusan Resavac
-   Roland Bauer

## Ziel / Ergebnis

Das Ziel / Ergebnis dieses Projekts besteht darin, Filmrezensionen beliebiger Filme auf eine einfache sowie anschauliche Art zusammenzufassen, sodass der Konsens verschiedener Meinungen auf einem einzigen Blick ersichtbar ist. Dies wird anhand einer Webapplikation zum Anzeigen einer Schlagwortwolke (Word Cloud) realisiert, welche die, aus den Filmrezensionen am häufigst vorkommenden, Adjektive darstellt (wobei max. die 20 am häufigst vorkommenden Adjektive verwendet werden, um eine einfache Lesbarkeit der Word Cloud sicherzustellen). Die Größe des Wortes steht dabei proportional zu dessen Häufigkeit.

## Architektur

Die Architektur dieses Projekts ist folgendermaßen aufgebaut:

![Architektur](architecture.png)

Dementsprechend gibt es **4 Microservices** mit **Kafka** als zentralen Message Broker. 

Um ein besseres Verständnis für diese Microservices zu schaffen, werden sie in den kommenden Absätzen genauer beschrieben: 

### 1. Streamlit Script (siehe in der Architektur rechts unten):

Das Streamlit Script (in der Verzeichnisstruktur unter worldcloud_app zu finden) stellt das Frontend des Projekts dar. Dabei kann der/die Endbenutzer*in 3 verschiedene Aktionen ausführen:
   - Er/Sie kann einen beliebigen Filmtitel eingeben und sich somit die Word Cloud der dazugehörigen Filmrezensionen anzeigen lassen,  
   - sich die Word Cloud der Filmrezensionen des aktuell populärsten Films anzeigen lassen (dieser wird täglich aktualisiert) und
   - die Caching-Datenbank leeren.
       
### 2. Filme Script (siehe in der Architektur rechts oben):

Das Filme Script (in der Verzeichnisstruktur unter movie_script zu finden) empfängt die Anfragen für neue Filmrezensionen via Kafka vom Streamlit Script, holt sich die notwendigen Daten (= ID des Films, Titel des Films und Bewertungen des Films) aus der Movie DB und sendet diese zurück an Kafka.
   
### 3. Wörterbuch Script (siehe in der Architektur links oben):

Das Wörterbuch Script (in der Verzeichnisstruktur unter dictionary_script zu finden) lädt beim Starten des Containers, je nach übergebenem Argument (über docker-compose.yml konfigurierbar), die Adjektive aus der entsprechenden Quelle, empfängt die Anfragen via Kafka vom Filme Script, filtert die Filmrezensionen nach deren Adjektiven und sendet schließlich die gefilterten Rezensionen gemeinsam mit der ID des Films und dem Titel des Films zurück an Kafka.

### 4. Spark Script (siehe in der Architektur links unten):

Das Spark Script (in der Verzeichnisstruktur unter Spark_script zu finden) wird für einerseits für Analysezwecke verwendet, dh. es
   - vereint die json-Dateien, die eine mögliche Quelle für Adjektive darstellen und transformiert den Inhalt in eine einzelne json-Datei, 
   - ermittelt die Anzahl aller adjektivischer Bedeutungen jedes Wortes und
   - gibt die Anzahl an Wörtern zurück, die zumindest eine adjektivische Bedeutung haben.

Andererseits empfängt es aber auch neue Anfragen (gefiltert) via Kafka vom Wörterbuch Script, macht ein Wordcount der Adjektive und sendet die empfangenen Daten und die Wordcounts wieder an Kafka. 

Um ebenfalls ein besseres Verständnis für Kafka als zentralen Message Broker zu schaffen, werden im kommen Absatz die einzelnen Kafka Topics beschrieben: 

### 1. "new_movie_title": 

Streamlit Script --> Filme Script

### 2. "movie_reviews": 

Filme Script --> Wörterbuch Script 

### 3. "adjectives": 

Wörterbuch Script --> Spark Script 

### 4. "adjectives_counted": 

Spark Script --> Streamlit Script

## Metadatenmodell
Um einen genaueren Einblick in die verwendeten Daten dieses Projekts zu gewähren, folgt eine Zusammenfassung der Felder aus Dateien, Kafka-Nachrichten und API-Anworten: 

### Filme Script:
Um präzise Filmdaten abrufen zu können, wird die sogenannte "themoviedb" (in der Achitektur unter Movie DB zu finden) verwendet (siehe: https://www.themoviedb.org/documentation/api). Wie bereits erwähnt, bietet die Webapplikation des Projekts den Nutzern u.a. die Möglichkeiten einen Filmtitel einzugeben und sich die Word Cloud aus dessen Filmrezensionen oder sich die Word Cloud des aktuell populärsten Films anzeigen zu lassen. In beiden Fällen sind die folgenden Informationen notwendig: 

- **original_title** - ``String``: Der Originaltitel des Films, der sich im *title* Feld unterscheiden kann. Wenn z.B. nach "Puss in boots" gewsucht und der Sprachparameter auf "de-DE" gesetzt wird, lautet der "original_title" "Puss in boots" und der "title" "Der gestiefelte Kater".

- **id** - ``Integer``: Eindeutiger Bezeichner für Filme. 

- **content** - ``String``: Der Text einer Rezension. 

Die Kernfunktion wird beim Empfang ausgeführt: 

- entweder **get_most_pop** - ``String``: Einfache Zeichenkette, die nach Bewertungen für einen der derzeit beliebtesten Filme fragt. In diesem Fall werden keine weiteren Informationan angegeben. 

- oder **movie-title** - ``String``: Gibt an, dass Bewertungen für eine gegebene Zeichenkette, die teilweise oder vollständig mit einem Filmtitel übereinstimmt, angefordert werden. Nach dieser Zeichenfolge folgt die Benutzereingabe. 

Das Filme Script extrahiert alle Wörter aus jeder Rezension und behält dabei im Auge, welche Wortliste zu welcher Rezension gehört --> Liste von Listen für Analysezwecke oder zukünftige Funktionen. Anschließend sendet es 3 wichtige Variablen an Kafka:

- **movie_id** - ``Integer``: Eindeutiger Bezeichner für Filme.
- **title** - ``String``: Der Originaltitel des Films.
- **reviews** - ``[[String String, ...], [...], ...]``: Die Liste der Listen mit allen Wörtern pro Rezension.

### Wörterbuch Script:
tbd

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
