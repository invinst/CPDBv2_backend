#!/usr/bin/env bash

docker-compose run web sh -c "coverage run cpdb/manage.py test && coverage report && coverage html"
