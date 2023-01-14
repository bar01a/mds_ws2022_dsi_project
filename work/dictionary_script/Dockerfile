# Dockerfile

# build the image
# run command from the root of the project
# docker build --no-cache -t dsi_dictionary -f work/dictionary_script/Dockerfile work/dictionary_script

# run the container
# docker run -p 8503:8503 --net jupyter-network dsi_dictionary

FROM python:3.9-slim

EXPOSE 8503

WORKDIR /dict

COPY Kafka_Helpers.py Kafka_Helpers.py
COPY dictionary_script.py dictionary_script.py
COPY requirements.txt requirements.txt
COPY data data
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python", "dictionary_script.py"]
