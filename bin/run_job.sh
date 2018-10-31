#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Run a job on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <manifest_file> <job_name> <backend_image_tag>"
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
    echo "Must specify manifest file as second argument."
    exit 1
else
    MANIFEST_FILE="$2"
fi

if [ -z "$3" ]; then
    echo "Must specify job name as third argument."
    exit 1
else
    JOB_NAME="$3"
fi

if [ -z "$4" ]; then
    echo "Must specify backend image tag as fourth argument."
    exit 1
else
    imagetag="$4"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

BACKEND_IMAGE_TAG=$imagetag templater kubernetes/jobs/$MANIFEST_FILE -f $ENV_FILE | kubectl apply -f - --namespace $NAMESPACE
SUCCEEDED=0
printf "The job output will be printed as soon as it's done. Please be patient...\n"
while [ "$SUCCEEDED" != "1" ]
do
  printf "."
  FAILED=$(kubectl get jobs $JOB_NAME -n $NAMESPACE -o go-template --template={{.status.failed}})
  if [ "$FAILED" == "1" ]; then
    printf "\nJob failed with following error:\n"
    kubectl logs -l job-name=$JOB_NAME -n $NAMESPACE
    kubectl delete job $JOB_NAME -n $NAMESPACE
    exit 1
  fi
  SUCCEEDED=$(kubectl get jobs $JOB_NAME -n $NAMESPACE -o go-template --template={{.status.succeeded}})
  sleep 10
done
printf "\n"
kubectl logs -l job-name=$JOB_NAME -n $NAMESPACE
kubectl delete job $JOB_NAME -n $NAMESPACE
