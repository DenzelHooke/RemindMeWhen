FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY celery.sh .
COPY requirements.txt .
RUN export PYTHONPATH=/usr/src/app/web/
RUN pip install -r requirements.txt

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "nano"]

CMD ["./celery.sh"]