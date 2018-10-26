FROM mdillon/postgis:9.6-alpine

USER $POSTGRES_USER

ENV POSTGRES_APP_DB cpdb
ENV POSTGRES_APP_USER cpdb
ENV POSTGRES_APP_PASSWORD password
ENV POSTGRES_NUMERACY_PASSWORD numeracy
ENV POSTGRES_NOTEBOOK_PASSWORD notebook
ENV POSTGRES_CIVIS_PASSWORD civis

ADD server.crt /var/lib/postgresql/ssl/
ADD server.key /var/lib/postgresql/ssl/
ADD postgresql.conf /etc/postgresql/

RUN chown postgres /var/lib/postgresql/ssl/server.crt && chmod 0600 /var/lib/postgresql/ssl/server.crt
RUN chown postgres /var/lib/postgresql/ssl/server.key && chmod 0600 /var/lib/postgresql/ssl/server.key

COPY init-scripts/* /docker-entrypoint-initdb.d/

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
