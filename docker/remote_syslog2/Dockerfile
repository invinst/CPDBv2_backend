FROM alpine

# Install rsyslog and rsyslog-tls
RUN apk update && \
    apk add rsyslog rsyslog-tls

# Download papertrail CA file
ADD https://papertrailapp.com/tools/papertrail-bundle.pem /etc/papertrail-bundle.pem
RUN chmod 0644 /etc/papertrail-bundle.pem

# Add papertrail config to rsyslog
ADD papertrail.conf /etc/rsyslog.d/95-papertrail.conf
RUN chmod 0644 /etc/rsyslog.d/95-papertrail.conf

# Install remote-syslog2
ADD https://github.com/papertrail/remote_syslog2/releases/download/v0.20/remote_syslog_linux_amd64.tar.gz .
RUN tar xzf ./remote_syslog_linux_amd64.tar.gz && \
    cd remote_syslog && \
    cp ./remote_syslog /usr/local/bin

# Add remote syslog config
ADD log_files.yml /etc/log_files.yml
RUN chmod 0644 /etc/log_files.yml

CMD remote_syslog -D --tls
