FROM python:3.6
RUN apt-get update
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
ENV FLASK_APP=src/server.py
EXPOSE 5000
CMD python /src/server.py