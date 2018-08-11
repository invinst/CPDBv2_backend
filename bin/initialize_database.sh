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
        --username "$PG_LOGIN@$PG_HOST" --host="$PG_HOST" --port=5432 --dbname postgres <<-EOSQL
    CREATE USER $APP_LOGIN;
    ALTER USER $APP_LOGIN WITH ENCRYPTED PASSWORD '$APP_PASS';
    DROP DATABASE $APP_DB;
    CREATE DATABASE $APP_DB WITH ENCODING 'UTF8' LC_COLLATE='en-US' LC_CTYPE='en-US' TEMPLATE=template0;
    GRANT $APP_DB TO $PG_LOGIN;
    GRANT ALL PRIVILEGES ON DATABASE $APP_DB TO $APP_LOGIN;
    CREATE EXTENSION postgis;
    CREATE USER $NUMERACY_LOGIN;
    ALTER USER $NUMERACY_LOGIN WITH ENCRYPTED PASSWORD '$NUMERACY_PASSWORD';
    CREATE USER $NOTEBOOK_LOGIN;
    ALTER USER $NOTEBOOK_LOGIN WITH ENCRYPTED PASSWORD '$NOTEBOOK_PASSWORD';
EOSQL

if [ $# -gt 1 ]; then
    PGPASSWORD=$PG_PASSWORD psql \
        --username "$PG_LOGIN@$PG_HOST" --host="$PG_HOST" --port=5432 $APP_DB < $2;
fi
