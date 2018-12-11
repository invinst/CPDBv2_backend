#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Connect to app database on production or staging or local using psql."
    echo ""
    echo "Usage: `basename $0` {--production|--staging|--local(default)}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    SERVICE=pg-proxy
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
    SERVICE=pg-proxy
else
    ENV_FILE=.env
    SERVICE=postgres
fi

source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

docker-compose up -d $SERVICE
docker-compose run psql psql -U postgres -h $SERVICE $POSTGRES_APP_DB

if [ "$SERVICE" == "pg-proxy" ]; then
    docker-compose kill pg-proxy
fi
