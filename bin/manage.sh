#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Run manage command."
    echo ""
    echo "Usage: `basename $0` {--production|--staging|--local} <command>"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify either --production or --staging or --local."
    exit 1
elif [ "$1" == "--production" ]; then
    NAMESPACE=production
elif [ "$1" == "--staging" ]; then
    NAMESPACE=staging
elif [ "$1" == "--local" ]; then
    shift
    docker-compose run web cpdb/manage.py $@
    exit 0
else
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

POD_NAME="$(kubectl get pods --selector=app=gunicorn -n $NAMESPACE --output=jsonpath={.items..metadata.name})"
shift
kubectl exec -it -n $NAMESPACE $POD_NAME cpdb/manage.py -- $@
