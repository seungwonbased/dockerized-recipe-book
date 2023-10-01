FROM ubuntu:20.04

WORKDIR /recipe-book

COPY . .

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt install -y python3-pip
RUN pip install wheel
RUN pip install -r requirements.txt

ENV FLASK_APP=app
ENV FLASK_DEBUG=true
ENV APP_CONFIG_FILE=/recipe-book/config/docker.py

CMD [ "gunicorn", "--bind", "0:5000", "app:create_app()" ]
# CMD [ "gunicorn", "--bind", "unix:/tmp/recipe-book.sock", "app:create_app()" ]
