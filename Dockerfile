# https://www.pybootcamp.com/blog/how-to-write-dockerfile-python-apps/
FROM python:3.12-slim-bullseye

ENV TINI_VERSION="v0.19.0"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /srv/app

RUN useradd -m -r tdevops && \
    chown tdevops /srv/app

USER tdevops 
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY src/api.py ./

ENTRYPOINT ["/tini", "--"]
