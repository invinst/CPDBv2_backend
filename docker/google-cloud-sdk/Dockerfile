FROM google/cloud-sdk

RUN echo "deb https://dl.bintray.com/sobolevn/deb git-secret main" | tee -a /etc/apt/sources.list && \
  curl https://api.bintray.com/users/sobolevn/keys/gpg/public.key | apt-key add -

RUN apt-get update

RUN apt-get install gawk git-secret gettext-base -y
