#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Schedule the cronjobs on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <django_command> <schedule> <backend_image_tag>"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging update_documents @daily latest"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify either --production or --staging."
    exit 1
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    NAMESPACE=production
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
    NAMESPACE=staging
else
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify manifest file as second argument."
    exit 1
else
    CRONJOB_COMMAND="$2"
fi

if [ -z "$3" ]; then
    echo "Must specify cronjob schedule as third argument."
    exit 1
else
    CRONJOB_SCHEDULE="$3"
fi

if [ -z "$4" ]; then
    echo "Must specify backend image tag as fourth argument."
    exit 1
else
    IMAGE_TAG="$4"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

CRONJOB_NAME="$(echo $CRONJOB_COMMAND | tr -s '_' | tr '_' '-')"

export BACKEND_IMAGE_TAG=$IMAGE_TAG
source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)
export CRONJOB_NAME=$CRONJOB_NAME
export CRONJOB_COMMAND=$CRONJOB_COMMAND
export CRONJOB_SCHEDULE=$CRONJOB_SCHEDULE

cat kubernetes/cronjob.yml | envsubst | kubectl apply -f - --namespace $NAMESPACE
kubectl get cronjobs -n $NAMESPACE
