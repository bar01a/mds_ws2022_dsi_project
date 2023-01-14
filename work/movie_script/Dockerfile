# Dockerfile

# build the image
# run command from the root of the project
# docker build --no-cache -t dsi_movie_script -f work/movie_script/Dockerfile work/movie_script

# run the container
# docker run -p 8503:8503 --net jupyter-network dsi_movie_script

FROM python:3.9-slim

EXPOSE 8504

WORKDIR /movie-script

COPY Kafka_Helpers.py Kafka_Helpers.py
COPY movie_script.py movie_script.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python", "movie_script.py"]
