FROM hashicorp/terraform

# Install gnupg and miscelaneous packages
RUN apk update && \
    apk add gnupg git bash py-pip make

# Install git-secret
RUN git clone https://github.com/sobolevn/git-secret.git git-secret && \
    cd git-secret && \
    make build  && \
    PREFIX="/usr/local" make install
