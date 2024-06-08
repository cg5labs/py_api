# https://www.pybootcamp.com/blog/how-to-write-dockerfile-python-apps/
#FROM python:3.12-slim-bullseye
FROM python:latest

WORKDIR /srv/app

RUN useradd -m -r tdevops && \
    chown tdevops /srv/app

USER tdevops 
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY src/app.py ./
COPY src/api.py ./
COPY src/db.py ./
COPY src/sql_models.py ./
COPY src/generate_key.py ./
COPY src/crud.py ./

RUN mkdir app-data && \ 
    chown tdevops /srv/app/app-data

ENTRYPOINT ["python3", "api.py" ]
