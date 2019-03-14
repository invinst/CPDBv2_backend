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

for cronjob_name in $(kubectl get cronjobs -o custom-columns=:.metadata.name -n $NAMESPACE)
do
    kubectl delete cronjob $cronjob_name -n $NAMESPACE &
done
