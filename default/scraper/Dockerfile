FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /etc/scrapyd/

WORKDIR /usr/src/scraper

COPY ./scraper/remind_me_scraper/scrapd.conf /etc/scrapyd/


COPY requirements.txt .
RUN pip install -r requirements.txt

RUN ["bash"]
RUN ["apt-get ", "update"]
RUN ["apt-get ", "install ", "-y ", "vim"]
