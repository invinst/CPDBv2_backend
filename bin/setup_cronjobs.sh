#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Schedule all cronjobs on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <backend_image_tag>"
    echo "       `basename $0` {-h|--help}"
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
    echo "Must specify backend image tag as second argument."
    exit 1
else
    imagetag="$2"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

export BACKEND_IMAGE_TAG=$imagetag
source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

kubectl delete cronjob --all -n $NAMESPACE
for manifest_file in kubernetes/cronjobs/*.yml; do
    cat $manifest_file | envsubst | kubectl apply -f - --namespace $NAMESPACE
done
