FROM alpine

ENV KUBE_LATEST_VERSION="v1.11.3"

# Install kubectl
RUN apk add --update ca-certificates \
 && apk add --update -t deps curl \
 && curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_LATEST_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl \
 && apk del --purge deps \
 && rm /var/cache/apk/*

# Install GPG & git
RUN apk add --update \
  gnupg \
  git \
  make \
  bash \
  curl

# Install Git secret
RUN git clone https://github.com/sobolevn/git-secret.git git-secret \
  && cd git-secret && make build \
  && PREFIX="/usr/local" make install

# Install templater
RUN curl -L https://raw.githubusercontent.com/johanhaleby/bash-templater/master/templater.sh -o /usr/local/bin/templater \
  && chmod +x /usr/local/bin/templater
