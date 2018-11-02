#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Connect to app database on production or staging or local using psql."
    echo ""
    echo "Usage: `basename $0` {--production|--staging|--local}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
elif [ "$1" == "--local" ]; then
    ENV_FILE=local.env
else
    echo "Must specify either --production or --staging or --local."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source $ENV_FILE

PGPASSWORD=$POSTGRES_APP_PASSWORD psql \
    --username $POSTGRES_APP_USER --host="$POSTGRES_HOST" --port=5432 $POSTGRES_APP_DB
