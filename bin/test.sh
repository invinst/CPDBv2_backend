#!/usr/bin/env bash

docker-compose run web python -m lambda.test
bin/manage.sh --local makemigrations --dry-run && bin/manage.sh --local test $@
