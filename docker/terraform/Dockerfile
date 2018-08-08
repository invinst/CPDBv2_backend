FROM hashicorp/terraform

# Install gnupg and miscelaneous packages
RUN apk update && \
    apk add gnupg git bash py-pip make

# Install git-secret
RUN git clone https://github.com/sobolevn/git-secret.git git-secret && \
    cd git-secret && \
    make build  && \
    PREFIX="/usr/local" make install

# Install azure cli
RUN apk add --virtual=build gcc libffi-dev musl-dev openssl-dev python-dev && \
    pip install azure-cli && \
    apk del --purge build
