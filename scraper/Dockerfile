FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/scraper

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install git+https://github.com/scrapy/scrapyd-client.git


WORKDIR /usr/src/scraper/remind_me_scraper

COPY . .


RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim-tiny"]

