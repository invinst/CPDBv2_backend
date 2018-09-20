FROM python:2.7-alpine

ENV GUNICORN_BIND 0.0.0.0:80
ENV GUNICORN_WORKERS 1
ENV GUNICORN_MAX_REQUESTS 0
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_NAME cpdb
ENV GUNICORN_LOGLEVEL info
ENV GUNICORN_CHDIR /usr/src/app/cpdb

ENV DJANGO_SETTINGS_MODULE config.settings.local

RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
    echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk add \
        postgresql-dev \
        gcc \
        libffi-dev \
        musl-dev \
        libressl-dev \
        g++ \
        build-base \
        python-dev \
        jpeg-dev \
        zlib-dev \
        proj4-dev@testing \
        gdal-dev@testing

ADD http://download.osgeo.org/geos/geos-3.6.1.tar.bz2 .
RUN tar xjf geos-3.6.1.tar.bz2 && \
    cd geos-3.6.1 && \
    ./configure && \
    make && \
    make install

WORKDIR /usr/src/app

ADD requirements requirements
RUN pip install --no-cache-dir -r requirements/local.txt

COPY . .

RUN adduser -D gunicorn
RUN chown -R gunicorn .
USER root

EXPOSE 80

CMD [ "gunicorn", "--config", "/usr/src/app/gunicorn.conf", "config.wsgi" ]
