# syntax = docker/dockerfile:experimental

FROM python:3.10-slim-buster

RUN apt update && apt install -y build-essential git gcc python-dev && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip

COPY ./requirements.txt ./code/requirements.txt

RUN python3 -m venv /venv

RUN --mount=type=cache,target=/root/.cache \
    . /venv/bin/activate && \
    pip install -r /code/requirements.txt

ENV PATH /venv/bin:/bin:/usr/bin:/usr/local/bin
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONPATH /code
ENV PYTHONUNBUFFERED 1
ENV PYTHONWARNINGS ignore

COPY . /code/

WORKDIR /code

LABEL Description="Boost.org Content Converter" Vendor="REVSYS"
