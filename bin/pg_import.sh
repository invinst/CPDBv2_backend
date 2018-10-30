#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Import SQL dump into PostgreSQL database."
    echo ""
    echo "Usage: `basename $0` {--production|--staging|--local} infile"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify either --production or --staging or --local."
    exit 1
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    exit 0
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
elif [ "$1" == "--local" ]; then
    ENV_FILE=local.env
else
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify infile."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source $ENV_FILE

PGPASSWORD=$POSTGRES_APP_PASSWORD psql \
    --username $POSTGRES_APP_USER --host="$POSTGRES_HOST" --port=5432 $POSTGRES_APP_DB < $2
