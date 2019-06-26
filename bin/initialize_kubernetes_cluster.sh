#!/bin/bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Initialize kubernetes cluster."
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

kubectl apply -f kubernetes/namespaces.yml
kubectl apply -f kubernetes/secrets-$NAMESPACE.yml

# Create nginx ingress controller
kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user $(gcloud config get-value account)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/cloud-generic.yaml
cat kubernetes/ingress.yml | envsubst | kubectl apply -f - -n $NAMESPACE
kubectl apply -f kubernetes/redirect-ingress.yml

# Deploy cloud sql proxy
cat kubernetes/pg_proxy.yml | envsubst | kubectl apply -f - -n $NAMESPACE

# Deploy Elasticsearch
kubectl apply -f kubernetes/elasticsearch.yml -n $NAMESPACE

# Deploy Redis
kubectl apply -f kubernetes/redis.yml -n $NAMESPACE

# Deploy backend
echo "Specify backend image tag:"
read backendtag
export BACKEND_IMAGE_TAG=$backendtag
cat kubernetes/gunicorn.yml | envsubst | kubectl apply -f - -n $NAMESPACE
