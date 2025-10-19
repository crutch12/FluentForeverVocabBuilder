# FROM python:3
# FROM python:3.8.18
FROM python:3.9
# FROM python:2.7

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

WORKDIR /app

RUN python -m venv venv

RUN bash venv/bin/activate

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["bash", "start.sh"]