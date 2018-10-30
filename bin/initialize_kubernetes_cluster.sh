#!/bin/bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Initialize kubernetes cluster."
    echo ""
    echo "Usage: `basename $0` {--production|--staging}"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ "$1" == "--production" ]; then
    ENV_FILE=prod.env
    NAMESPACE=production
    exit 0
elif [ "$1" == "--staging" ]; then
    ENV_FILE=staging.env
    NAMESPACE=staging
else
    echo "Must specify either --production or --staging."
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
source $ENV_FILE

kubectl apply -f kubernetes/namespaces.yml
kubectl apply -f kubernetes/secrets.yml -n $NAMESPACE

# Create nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/cloud-generic.yaml
templater kubernetes/ingress.yml -f $ENV_FILE | kubectl apply -f - -n $NAMESPACE

# Deploy postgres
echo "Specify postgres image tag:"
read postgrestag
POSTGRES_IMAGE_TAG=$postgrestag templater kubernetes/postgres.yml -f $ENV_FILE | kubectl apply -f - -n $NAMESPACE

# Deploy Elasticsearch
kubectl apply -f kubernetes/elasticsearch.yml -n $NAMESPACE

# Deploy Redis
kubectl apply -f kubernetes/redis.yml -n $NAMESPACE

# Deploy backend
echo "Specify backend image tag:"
read backendtag
BACKEND_IMAGE_TAG=$backendtag templater kubernetes/gunicorn.yml -f $ENV_FILE | kubectl apply -f - -n $NAMESPACE
