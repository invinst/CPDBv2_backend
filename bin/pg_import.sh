#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

FILE_DIR="$(cd "$(dirname "$2")"; pwd)"

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
    SERVICE=pg-proxy
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
    SERVICE=pg-proxy
elif [ "$1" == "--local" ]; then
    ENV_FILE=.env
    SERVICE=postgres
else
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify infile."
    exit 1
fi

source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

docker-compose up -d $SERVICE
docker-compose run -v $FILE_DIR:/app psql bash -c "psql -U postgres -h $SERVICE $POSTGRES_APP_DB < /app/$(basename $2)"

if [ "$SERVICE" == "pg-proxy" ]; then
    docker-compose kill pg-proxy
fi
