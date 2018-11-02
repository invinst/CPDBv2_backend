FROM python:2.7-slim

ENV GUNICORN_BIND 0.0.0.0:80
ENV GUNICORN_WORKERS 1
ENV GUNICORN_MAX_REQUESTS 0
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_NAME cpdb
ENV GUNICORN_LOGLEVEL info
ENV GUNICORN_CHDIR /usr/src/app/cpdb

RUN apt-get update && \
    apt-get install -y \
    gcc \
    proj-bin \
    gdal-bin \
    build-essential \
    libjpeg-dev \
    curl \
    zlib1g-dev

ADD http://download.osgeo.org/geos/geos-3.6.1.tar.bz2 .
RUN tar xjf geos-3.6.1.tar.bz2 && \
    cd geos-3.6.1 && \
    ./configure && \
    make && \
    make install && \
    rm -rf /geos-3.6.1 && \
    rm /geos-3.6.1.tar.bz2

WORKDIR /usr/src/app

ADD requirements requirements
RUN pip install --no-cache-dir -r requirements/local.txt

COPY . .

RUN mkdir cpdb/static

RUN useradd -ms /bin/bash gunicorn
RUN chown -R gunicorn .
RUN mkdir /logfiles && chown gunicorn /logfiles
USER root

EXPOSE 80

CMD [ "gunicorn", "--config", "/usr/src/app/gunicorn.conf", "config.wsgi" ]
