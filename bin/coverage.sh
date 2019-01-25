#!/usr/bin/env bash
docker-compose run web python -m lambda.test
docker-compose run web sh -c "cpdb/manage.py makemigrations --dry-run && coverage run cpdb/manage.py test && coverage report && coverage html"
