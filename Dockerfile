FROM python:3.10.8-slim

LABEL maintainer="sasha.syrota15@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p "/files/media" &&  \
    mkdir -p "/files/static"

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /files/media &&  \
    chown -R my_user /files/static

RUN chmod -R 755 /files/media && \
    chmod -R 755 /files/static

