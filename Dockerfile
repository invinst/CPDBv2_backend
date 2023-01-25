FROM python:3.7-slim

ENV GUNICORN_BIND 0.0.0.0:80
ENV GUNICORN_WORKERS 1
ENV GUNICORN_MAX_REQUESTS 0
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_NAME cpdb
ENV GUNICORN_LOGLEVEL info
ENV GUNICORN_CHDIR /usr/src/app/cpdb
ENV PAPERTRAIL_CA_FILE /etc/papertrail-bundle.pem

RUN apt-get update && \
    apt-get install -y \
    gcc \
    proj-bin \
    gdal-bin \
    build-essential \
    libjpeg-dev \
    curl \
    zlib1g-dev \
    git \
    zip \
    python3-dev \
    musl-dev \
    libpq-dev

RUN pip install poetry

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY poetry.lock poetry.lock

RUN poetry install

# This was required by gdal-bin but now it is provided by libgeos-3.9.0/stable
# RUN curl http://download.osgeo.org/geos/geos-3.6.1.tar.bz2 | tar xjv && \
#     cd geos-3.6.1 && \
#     ./configure && \
#     make && \
#     make install && \
#     cd - && \
#     rm -rf geos-3.6.1

RUN curl -o $PAPERTRAIL_CA_FILE https://papertrailapp.com/tools/papertrail-bundle.pem

COPY . .

RUN mkdir cpdb/static

RUN useradd -ms /bin/bash gunicorn
RUN chown -R gunicorn .
USER root

EXPOSE 80

CMD [ "poetry", "run", "gunicorn", "--config", "/usr/src/app/gunicorn.conf", "config.wsgi" ]
