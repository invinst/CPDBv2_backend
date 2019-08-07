#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Schedule the cronjobs on production or beta or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--beta|--staging} <django_command> <schedule> <backend_image_tag>"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging update_documents @daily latest"
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
    echo "Must specify kept cronjobs as second argument."
    exit 1
else
    KEPT_CRONJOBS="$2"
fi

echo "Kept cronjobs: $KEPT_CRONJOBS"

for cronjob_name in $(kubectl get cronjobs -o custom-columns=:.metadata.name -n $NAMESPACE)
do
    system_cronjob_name="${cronjob_name//-/_}"
    if ! [[ " ${KEPT_CRONJOBS[*]} " == *"$system_cronjob_name"* ]];
    then
      kubectl delete cronjob $cronjob_name -n $NAMESPACE &
    fi
done
