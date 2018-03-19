FROM circleci/python:2.7-jessie-node

USER root

############################################################################
# We also need ansible for deploying stuff
############################################################################

RUN pip install --upgrade pip
RUN pip install --upgrade pyOpenSSL ansible
RUN ansible-galaxy install azavea.postgresql


############################################################################
# Install much needed packages
############################################################################

RUN apt-get update \
    && apt-get install -y libav-tools binutils libproj-dev gdal-bin libncurses5 libncurses5-dev


############################################################################
# Run as non root user
############################################################################

RUN useradd -ms /bin/bash deploy

USER deploy
WORKDIR /home/deploy
ENV PATH /home/deploy/.local/bin:$PATH
