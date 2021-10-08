FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/remindme_scraper

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /usr/src/remindme_scraper/remind_me_scraper

COPY . .

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim-tiny"]

