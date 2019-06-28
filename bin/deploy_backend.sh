#!/bin/bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Deploy backend with input build-num."
    echo ""
    echo "Usage: `basename $0` {--production|--beta|--staging}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    NAMESPACE=production
elif [ "$1" == "--beta" ]; then
    ENV_FILE=beta.env
    NAMESPACE=beta
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
    NAMESPACE=staging
else
    echo "Must specify either --production or --beta or --staging."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)

# Deploy backend
echo "Specify backend image tag:"
read backendtag
export BACKEND_IMAGE_TAG=$backendtag
cat kubernetes/gunicorn.yml | envsubst | kubectl apply -f - -n $NAMESPACE
