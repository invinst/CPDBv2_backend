#!/usr/bin/env bash

docker-compose run --service-ports web cpdb/manage.py $@
