FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/remindme_web

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /usr/src/remindme_web/remind_me_django

COPY . .

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim-tiny"]


