#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Schedule the cronjobs on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <cronjob_file> <backend_image_tag>"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging update_documents.yml latest"
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
    manifest_file="$2"
fi

if [ -z "$3" ]; then
    echo "Must specify backend image tag as third argument."
    exit 1
else
    imagetag="$3"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

export BACKEND_IMAGE_TAG=$imagetag
source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

cat kubernetes/cronjobs/$manifest_file | envsubst | kubectl apply -f - --namespace $NAMESPACE
kubectl get cronjobs -n $NAMESPACE
