FROM mdillon/postgis:9.6-alpine

USER $POSTGRES_USER

ENV POSTGRES_APP_DB cpdb
ENV POSTGRES_APP_USER cpdb
ENV POSTGRES_APP_PASSWORD password
ENV POSTGRES_NUMERACY_PASSWORD numeracy
ENV POSTGRES_NOTEBOOK_PASSWORD notebook
ENV POSTGRES_CIVIS_PASSWORD civis

ADD postgresql.conf /etc/postgresql/

COPY init-scripts/* /docker-entrypoint-initdb.d/

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
