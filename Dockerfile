# https://www.pybootcamp.com/blog/how-to-write-dockerfile-python-apps/
#FROM python:3.12-slim-bullseye
FROM alpine:latest

WORKDIR /srv/app

# Alpine
# Create a group and user
RUN addgroup -S tdevops && adduser -S tdevops -G tdevops --uid 1000 && \
    chown tdevops /srv/app

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add py3-pip

USER tdevops 
COPY requirements.txt ./
RUN python3 -m venv venv
RUN source venv/bin/activate && pip3 install -r requirements.txt

COPY src/app_init ./
COPY src/db_init ./
COPY src/generate_key ./
COPY src/app.py ./
COPY src/api.py ./
COPY src/db.py ./
COPY src/sql_models.py ./
COPY src/generate_key.py ./
COPY src/crud.py ./
COPY src/apm_config.py ./
COPY src/webserver.py ./

RUN mkdir app-data && \ 
    chown tdevops /srv/app/app-data
RUN mkdir log && \ 
    chown tdevops /srv/app/log

ENTRYPOINT ["/srv/app/app_init -p DEFAULT" ]
