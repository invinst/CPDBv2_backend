FROM mdillon/postgis:9.6-alpine

USER $POSTGRES_USER

ENV APPLICATION_DB cpdb
ENV APPLICATION_DB_USER cpdb
ENV APPLICATION_DB_PASSWORD password

COPY init-scripts/* /docker-entrypoint-initdb.d/
