#!/usr/bin/env bash
set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Run a job on production or beta or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--beta|--staging} <backend_image_tag> <django_command> [additional_flags]"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging latest rebuild_index"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify either --production or --beta or --staging."
    exit 1
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
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify backend image tag as second argument."
    exit 1
else
    IMAGE_TAG="$2"
fi

if [ -z "$3" ]; then
    echo "Must specify command as third argument."
    exit 1
else
    shift
    shift
    REST="$*"
    JOB_COMMAND="$1"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

JOB_NAME="$(echo $JOB_COMMAND | tr -s '_' | tr '_' '-')"
echo "Running $JOB_NAME with image cpdbdev/backend:$IMAGE_TAG"

export BACKEND_IMAGE_TAG=$IMAGE_TAG
source $ENV_FILE
export $(cut -d= -f1 $ENV_FILE)
export JOB_NAME
export COMMAND="$(echo $REST | sed 's/ /\", \"/g')"

cat kubernetes/job.yml | envsubst | kubectl delete -f - -n $NAMESPACE || true

trap stop_job_or_not 2

function stop_job_or_not() {
    dodelete=n
    echo "Do you want to stop job as well? (y|N)"
    read dodelete
    dodelete_lower="$(echo $dodelete | tr '[:upper:]' '[:lower:]')"
    if [ "$dodelete_lower" == "y" ]; then
        kubectl delete job $JOB_NAME -n $NAMESPACE
    fi
    exit 0
}

JOB_STATUS="$(cat kubernetes/job.yml | envsubst | kubectl apply -f - --namespace $NAMESPACE)"
echo $JOB_STATUS

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

if [ -n "$FAILED" ] && [ "$FAILED" -eq "$FAILED" ] 2>/dev/null; then
    exit 1
fi
