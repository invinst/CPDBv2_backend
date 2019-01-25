#!/usr/bin/env bash

bin/manage.sh --local makemigrations --dry-run && docker-compose run web python -m lambda.test && bin/manage.sh --local test $@
