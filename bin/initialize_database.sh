#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Initialize app database for production or staging,"
    echo "also loads from dump file if one is provided."
    echo ""
    echo "Usage: `basename $0` {--production|--staging}"
    echo "       `basename $0` {--production|--staging} sql_dump_file"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    PG_HOST=$(terraform output postgres_production_fqdn)
    PG_LOGIN=$(terraform output postgres_production_login)
    PG_PASSWORD=$(terraform output postgres_production_password)
elif [ "$1" == "--staging" ]; then
    PG_HOST=$(terraform output postgres_staging_fqdn)
    PG_LOGIN=$(terraform output postgres_staging_login)
    PG_PASSWORD=$(terraform output postgres_staging_password)
else
    echo "Must specify either --production or --staging."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source prod.env

PGPASSWORD=$PG_PASSWORD psql \
        --username "$PG_LOGIN@$PG_HOST" --host="$PG_HOST" --port=5432 "sslmode=require dbname=postgres" <<-EOSQL
    CREATE USER cpdb;
    ALTER USER cpdb WITH ENCRYPTED PASSWORD '$APP_PASSWORD';
    DROP DATABASE cpdb;
    CREATE DATABASE cpdb WITH ENCODING 'UTF8' LC_COLLATE='en-US' LC_CTYPE='en-US' TEMPLATE=template0;
    GRANT cpdb TO $PG_LOGIN;
    GRANT ALL PRIVILEGES ON DATABASE cpdb TO cpdb;
    CREATE EXTENSION postgis;
    CREATE USER numeracy;
    ALTER USER numeracy WITH ENCRYPTED PASSWORD '$NUMERACY_PASSWORD';
    CREATE USER notebook;
    ALTER USER notebook WITH ENCRYPTED PASSWORD '$NOTEBOOK_PASSWORD';
EOSQL

if [ $# -gt 1 ]; then
    PGPASSWORD=$PG_PASSWORD psql \
        --username "$PG_LOGIN@$PG_HOST" --host="$PG_HOST" --port=5432 "sslmode=require dbname=cpdb" < $2;
fi
