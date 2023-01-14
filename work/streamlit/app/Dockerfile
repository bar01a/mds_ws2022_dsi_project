# app/Dockerfile

# build the image
# run command from the root of the project
# docker build --no-cache -t dsi_streamlit_app -f work/streamlit/app/Dockerfile work/streamlit/app

# run the container
# docker run -p 8501:8501 --net jupyter-network dsi_streamlit_app

FROM python:3.9-slim

EXPOSE 8501

WORKDIR /app

COPY Kafka_Helpers.py Kafka_Helpers.py
COPY wordcloud_app.py wordcloud_app.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "wordcloud_app.py", "--server.port=8501", "--server.address=0.0.0.0"]