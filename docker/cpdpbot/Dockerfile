FROM python:3.5-jessie

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get dist-upgrade -y && \
    apt-get install build-essential software-properties-common gcc -y

RUN apt-get -qq update && apt-get -y install \
    libcairo2-dev \
    libffi-dev \
    libjpeg-turbo-progs \
    libtiff5-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    libharfbuzz-dev \
    libssl-dev \
    libfribidi-dev && \
    apt-get clean

RUN curl -o /etc/papertrail-bundle.pem https://papertrailapp.com/tools/papertrail-bundle.pem

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m imageio download_bin all

RUN mkdir -p /app/
COPY cpdpbot /app/cpdpbot
WORKDIR /app

ADD VERSION .

CMD ["python", "-m", "cpdpbot.tweet"]
