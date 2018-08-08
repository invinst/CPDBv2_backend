FROM hashicorp/terraform

RUN apk add gnupg git make bash

RUN git clone https://github.com/sobolevn/git-secret.git git-secret && \
    cd git-secret && \
    make build  && \
    PREFIX="/usr/local" make install
