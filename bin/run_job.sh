#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Run a job on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <manifest_file> <backend_image_tag>"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging rebuild_index.yml latest"
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
    MANIFEST_FILE="$2"
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

cat kubernetes/jobs/$MANIFEST_FILE | envsubst | kubectl delete -f - -n $NAMESPACE || true

JOB_STATUS="$(cat kubernetes/jobs/$MANIFEST_FILE | envsubst | kubectl apply -f - --namespace $NAMESPACE)"
echo $JOB_STATUS
JOB_NAME="$(echo $JOB_STATUS | sed -En 's/job.batch[ "\/]+([a-z-]+)"? .+/\1/p')"
echo $JOB_NAME

PHASE=Pending
while [ "$PHASE" == "Pending" ]
do
  PHASE=$(kubectl get pods -l job-name=$JOB_NAME -n $NAMESPACE -o go-template --template="{{(index .items 0).status.phase}}")
  sleep 1
done

NAME=$(kubectl get pods -l job-name=$JOB_NAME -n $NAMESPACE -o go-template --template="{{(index .items 0).metadata.name}}")
kubectl logs $NAME -n $NAMESPACE -f

FAILED=$(kubectl get jobs $JOB_NAME -n $NAMESPACE -o go-template --template={{.status.failed}})

kubectl delete job $JOB_NAME -n $NAMESPACE

if [ "$FAILED" == "1" ]; then
    exit 1
fi
