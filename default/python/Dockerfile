FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/


COPY requirements.txt .

RUN pip install -r requirements.txt

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
