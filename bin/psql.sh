#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Connect to app database on production or staging using psql."
    echo ""
    echo "Usage: `basename $0` {--production|--staging}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    PG_HOST=$(terraform output postgres_production_fqdn)
    PG_LOGIN=$(terraform output postgres_production_login)
    PG_PASSWORD=$(terraform output postgres_production_password)
    exit 0
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

PGPASSWORD=$(terraform output postgres_staging_password) psql \
    --username "$PG_LOGIN@$PG_HOST" --host="$PG_HOST" --port=5432 "sslmode=require dbname=$APP_DB"
